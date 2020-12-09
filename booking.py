import argparse  # noqa:D100
import datetime
import logging
import re

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from booking_parser import BookingParser
from data_base_operation import (is_hotel_exist, get_hotels_rating,
                                 get_years_opening_hotels,
                                 remove_extra_rows, get_hotels_from_city,
                                 get_important_facilities)
from data_base_setup import DBEngine
from graph_builder import (diagram_open_hotels, draw_map_by_coords,
                           schedule_quantity_rating, pie_chart_from_scores,
                           get_table_of_ratio_data, get_table_of_prices, get_table_of_prices_by_star)
from stat_methods import (group_hotels_by_scores, get_hotels_ratio)

session = requests.Session()
REQUEST_HEADER = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36")}
TODAY = datetime.datetime.now() + datetime.timedelta(0)
NEXT_DATE = TODAY + datetime.timedelta(1)
BOOKING_PREFIX = 'https://www.booking.com'
DATABASE = DBEngine

cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург',
          'Казань', 'Нижний Новгород', 'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону']
cities_in_english = ['Moscow', 'Saint_Petersburg', 'Novosibirsk', 'Yekaterinburg',
                     'Kazan', 'Nizhny_Novgorod', 'Chelyabinsk', 'Samara', 'Omsk', 'Rostov-on-Don']


def get_max_offset(soup: BeautifulSoup) -> int:
    """Get the number of hotel pages."""
    all_offset = []
    if soup.find_all('div', {'class': 'sr_header'}) is not None:
        all_offset = soup.find_all('div', {'class': 'sr_header'})[-1].get_text().strip().replace(u'\xa0', '')
        all_offset = round(int(re.search(r'\d+', all_offset).group()) / 25)
    return all_offset


def create_link(city: str, country: str, off_set: int, date_in: datetime.datetime, date_out: datetime.datetime) -> str:
    """Create a link to collect data."""
    month_in = date_in.month
    day_in = date_in.day
    year_in = date_in.year
    month_out = date_out.month
    day_out = date_out.day
    year_out = date_out.year
    count_people = 1

    url = "https://www.booking.com/searchresults.ru.html?checkin_month={checkin_month}" \
          "&checkin_monthday={checkin_day}" \
          "&checkin_year={checkin_year}" \
          "&checkout_month={checkout_month}" \
          "&checkout_monthday={checkout_day}" \
          "&checkout_year={checkout_year}" \
          "&group_adults={group_adults}" \
          "&group_children=0&order=score" \
          "&ss={city}%2C%20{country}" \
          "&offset={limit}" \
          "&selected_currency=RUB".format(
            checkin_month=month_in,
            checkin_day=day_in,
            checkin_year=year_in,
            checkout_month=month_out,
            checkout_day=day_out,
            checkout_year=year_out,
            group_adults=count_people,
            country=country,
            limit=off_set,
            city=city)
    logging.info(f'URL created: {url}')
    return url


def get_info(city: str,
             country: str,
             off_set: int,
             date_in: datetime.datetime,
             date_out: datetime.datetime) -> None:
    """Receives data by link."""
    url = create_link(city, country, off_set, date_in, date_out)
    logging.info(f"URL: {url}")
    response = session.get(url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    logging.info("Parser runs...")
    off_set = int(get_max_offset(soup))
    offset = 0
    if off_set > 0:
        for i in tqdm(range(off_set)):
            parsing_data(session, city, country, date_in, date_out, offset)
            offset += 25


def parsing_data(session: requests.Session, city: str, country: str, date_in: datetime.datetime,
                 date_out: datetime.datetime, off_set: int) -> None:
    """Gather information about a specific hotel."""
    data_url = create_link(city, country, off_set, date_in, date_out)
    response = session.get(data_url, headers=REQUEST_HEADER, timeout=5)
    soup = BeautifulSoup(response.text, "lxml")
    hotels = soup.select("#hotellist_inner div.sr_item.sr_item_new")

    for hotel in tqdm(hotels):
        parser = BookingParser(hotel)
        name = parser.name()
        city = parser.city()
        link = parser.detail_link()
        logging.info(f'Getting info for {name}.')
        if link is not None:
            try:
                detail_page_response = session.get(BOOKING_PREFIX + link, headers=REQUEST_HEADER, timeout=5)
            except Exception as e:
                logging.error(f"Failed with detail_page_response: {e}.")
                continue

            hotel_html = BeautifulSoup(detail_page_response.text, "lxml")
            open_date = parser.open_hotel_date(hotel_html)

            if is_hotel_exist(name, city, open_date):
                continue

            latitude = parser.coordinates(hotel_html)[0]
            longitude = parser.coordinates(hotel_html)[1]
            important_facilities = ', '.join(parser.important_facilites(hotel_html))
            neighborhood_structures = parser.neighborhood_structures(hotel_html)
            services_offered = parser.offered_services(hotel_html)
            extended_rating = parser.extended_rating(hotel_html)
            reviews = parser.review_rating(hotel_html)
            apartaments = parser.apartaments(hotel_html)

        rating = parser.rating()
        price = parser.price()
        image = parser.image()
        star = parser.star()
        logging.info('Connection to database.')
        try:
            with DATABASE.begin() as connection:
                logging.info('Inserting into table hotels.')
                connection.execute(
                    "insert into hotels (name, score, price, image, link, city, open_date, star) "
                    f"values ('{name}', '{rating}', '{price}', "
                    f"'{image}', '{link}', '{city}', '{open_date}', '{star}')")
                logging.info('Inserting into table coordinates.')
                connection.execute(
                    f"insert into coordinates (latitude, longitude) values ('{latitude}', '{longitude}')")
                logging.info('Inserting into table important_facilities')
                connection.execute(
                    "insert into important_facilities (important_facilities) "
                    f"values ('{important_facilities}')")
                logging.info('Getting hotel_id.')
                hotel_id = connection.execute(
                    "SELECT hotel_id FROM hotels WHERE hotel_id = (SELECT MAX(hotel_id)  FROM hotels)")
                hotel_id = hotel_id.fetchone()[0]

                logging.info('Inserting into table services_offered.')
                for service_offered in services_offered:
                    service_type = service_offered['type']
                    service_value = ', '.join(service_offered['value'])
                    connection.execute(
                        "insert into services_offered (services_offered, value, hotel_id) "
                        f"values ('{service_type}', '{service_value}', '{hotel_id}')")

                logging.info('Inserting into table neighborhood_structures.')
                for neighborhood_structure in neighborhood_structures:
                    name = neighborhood_structure['name']
                    structure_type = neighborhood_structure['structure_type']
                    distance = neighborhood_structure['distance']
                    connection.execute(
                        "insert into neighborhood_structures "
                        "(neighborhood_structure, structure_type, distance) "
                        f"values ('{name}', '{structure_type}', '{distance}')")

                logging.info('Inserting into table extended_rating.')
                for rating_name, rating_value in extended_rating.items():
                    connection.execute(
                        "insert into extended_rating (hotel_id, rating_name, rating_value) "
                        f"values ('{hotel_id}', '{rating_name}', '{rating_value}')")

                logging.info('Inserting into table review_rating.')
                for review_name, review_count in reviews.items():
                    connection.execute(
                        "insert into review_rating (hotel_id, review_rating_name, review_rating_count) "
                        f"values ('{hotel_id}', '{review_name}', '{review_count}')")

                logging.info('Inserting into table apartaments.')
                for apartament in apartaments:
                    name = apartament['name']
                    apartaments_price = apartament['price']
                    capacity = apartament['capacity']
                    connection.execute(
                        "insert into apartaments (hotel_id, apartaments_name, apartaments_price, hotel_beds) "
                        f"values ('{hotel_id}', '{name}', '{apartaments_price}', '{capacity}')")
            logging.info('Hotel added.')
        except Exception as e:
            logging.error(f"DB Error: {e}")
        logging.info('All rows added.')
        session.close()
    logging.info('Session close.')


def main(parse_new_data: bool, country: str) -> None:  # noqa:D100
    date_in = TODAY
    off_set = 1000
    date_out = NEXT_DATE
    remove_extra_rows()

    if parse_new_data:
        logging.info('Parsing new data.')
        for city in cities_in_english:
            get_info(city, country, off_set, date_in, date_out)

    draw_map_by_coords('DisplayAllHotels')

    rating = get_hotels_rating()
    schedule_quantity_rating(rating)

    years = get_years_opening_hotels()
    diagram_open_hotels(years)

    """Here we get hotels from spb and msc and draw pie chart about their scores"""
    spb = 'Санкт-Петербург'
    msk = 'Москва'
    hotels_in_spb = get_hotels_from_city(spb)
    hotels_in_moscow = get_hotels_from_city(msk)
    grouped_spb_hotels = group_hotels_by_scores(hotels_in_spb)
    grouped_moscow_hotels = group_hotels_by_scores(hotels_in_moscow)
    pie_chart_from_scores(grouped_spb_hotels, spb)
    pie_chart_from_scores(grouped_moscow_hotels, msk)
    important_facilities = get_important_facilities()
    get_table_of_prices(cities)
    get_table_of_prices_by_star(cities)
    """Here we get table with info about cities, amounts, population and ratio
        (amount of hotels in city to population of this city)"""
    hotels_ratio_info = get_hotels_ratio(cities)
    get_table_of_ratio_data(hotels_ratio_info)


if __name__ == "__main__":
    logging.basicConfig(handlers=[logging.FileHandler(filename="logs.log",
                                                      encoding='cp1251', mode='w')],
                        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        datefmt="%F %A %T",
                        level=logging.DEBUG)
    logging.getLogger('matplotlib.font_manager').disabled = True
    parser = argparse.ArgumentParser()
    parser.add_argument("--get-data",
                        action='store_true',
                        help='Used to parsing new data from booking.')
    parser.add_argument("--country", "-c",
                        help='Country for parsing.',
                        default='Russia')
    args = parser.parse_args()
    main(args.get_data, args.country)
