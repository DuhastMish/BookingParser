import argparse  # noqa:D100
import datetime
import logging
import re

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from booking_parser import BookingParser
from data_base_operation import (get_hotels_from_city, get_hotels_rating,
                                 get_years_opening_hotels, is_hotel_exist,
                                 remove_extra_rows_by_name)
from data_base_setup import DBEngine
from graph_builder import (diagram_open_hotels, draw_map_by_coords,
                           pie_chart_from_scores, schedule_quantity_rating)
from stat_methods import group_hotels_by_scores

session = requests.Session()
REQUEST_HEADER = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36")}
TODAY = datetime.datetime.now() + datetime.timedelta(0)
NEXT_DATE = TODAY + datetime.timedelta(1)
BOOKING_PREFIX = 'https://www.booking.com'
DATABASE = DBEngine


def get_max_offset(soup: BeautifulSoup) -> int:
    """Get the number of hotel pages."""
    all_offset = []
    if soup.find_all('div', {'class': 'sr_header'}) is not None:
        all_offset = soup.find_all('div', {'class': 'sr_header'})[-1].get_text().strip().replace(u'\xa0', '')
        all_offset = round(int(re.search(r'\d+', all_offset).group()) / 25)
    return all_offset


def create_link(country: str, off_set: int, date_in: datetime.datetime, date_out: datetime.datetime) -> str:
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
          "&group_children=0&order=popularity" \
          "&ss=%2C%20{country}" \
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
            limit=off_set)

    return url


def get_info(country: str, off_set: int, date_in: datetime.datetime, date_out: datetime.datetime) -> None:
    """Receives data by link."""
    url = create_link(country, off_set, date_in, date_out)
    response = session.get(url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    logging.warning(f"{TODAY.strftime('%H:%M:%S')}:: Начинаю собирать данные...")
    off_set = int(get_max_offset(soup))
    offset = 0
    if off_set > 0:
        for i in tqdm(range(off_set)):
            offset += 25
            parsing_data(session, country, date_in, date_out, offset)


def parsing_data(session: requests.Session, country: str, date_in: datetime.datetime,
                 date_out: datetime.datetime, off_set: int) -> None:
    """Gather information about a specific hotel."""
    data_url = create_link(country, off_set, date_in, date_out)
    response = session.get(data_url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    hotels = soup.select("#hotellist_inner div.sr_item.sr_item_new")

    for hotel in tqdm(hotels):
        parser = BookingParser(hotel)
        link = parser.detail_link()
        if is_hotel_exist(link):
            continue
        name = parser.name()
        rating = parser.rating()
        price = parser.price()
        image = parser.image()
        city = parser.city()
        star = parser.star()
        if link is not None:
            try:
                detail_page_response = session.get(BOOKING_PREFIX + link, headers=REQUEST_HEADER)
            except Exception as e:
                logging.warning(f"{TODAY.strftime('%H:%M:%S')}:: Failed with detail_page_response: {e}")
                continue
            hotel_html = BeautifulSoup(detail_page_response.text, "lxml")
            latitude = parser.coordinates(hotel_html)[0]
            longitude = parser.coordinates(hotel_html)[1]
            important_facilities = ', '.join(parser.important_facilites(hotel_html))
            neighborhood_structures = parser.neighborhood_structures(hotel_html)
            services_offered = parser.offered_services(hotel_html)
            open_date = parser.open_hotel_date(hotel_html)
            extended_rating = parser.extended_rating(hotel_html)
            reviews = parser.review_rating(hotel_html)
            apartaments = parser.apartaments(hotel_html)
        try:
            with DATABASE.begin() as connection:
                connection.execute(
                    "insert into hotels (name, score, price, image, link, city, open_date, star) "
                    f"values ('{name}', '{rating}', '{price}', "
                    f"'{image}', '{link}', '{city}', '{open_date}', '{star}')")
                connection.execute(
                    f"insert into coordinates (latitude, longitude) values ('{latitude}', '{longitude}')")
                connection.execute(
                    "insert into important_facilities (important_facilities) "
                    f"values ('{important_facilities}')")
                hotel_id = connection.execute(
                    "SELECT hotel_id FROM hotels WHERE hotel_id = (SELECT MAX(hotel_id)  FROM hotels)")
                hotel_id = hotel_id.fetchone()[0]

                for service_offered in services_offered:
                    service_type = service_offered['type']
                    service_value = ', '.join(service_offered['value'])
                    connection.execute(
                        "insert into services_offered (services_offered, value, hotel_id) "
                        f"values ('{service_type}', '{service_value}', '{hotel_id}')")

                for neighborhood_structure in neighborhood_structures:
                    name = neighborhood_structure['name']
                    structure_type = neighborhood_structure['structure_type']
                    distance = neighborhood_structure['distance']
                    connection.execute(
                        "insert into neighborhood_structures "
                        "(neighborhood_structure, structure_type, distance) "
                        f"values ('{name}', '{structure_type}', '{distance}')")

                for rating_name, rating_value in extended_rating.items():
                    connection.execute(
                        "insert into extended_rating (hotel_id, rating_name, rating_value) "
                        f"values ('{hotel_id}', '{rating_name}', '{rating_value}')")

                for review_name, review_count in reviews.items():
                    connection.execute(
                        "insert into review_rating (hotel_id, review_rating_name, review_rating_count) "
                        f"values ('{hotel_id}', '{review_name}', '{review_count}')")

                for apartament in apartaments:
                    name = apartament['name']
                    apartaments_price = apartament['price']
                    capacity = apartament['capacity']
                    connection.execute(
                        "insert into apartaments (hotel_id, apartaments_name, apartaments_price, hotel_beds) "
                        f"values ('{hotel_id}', '{name}', '{apartaments_price}', '{capacity}')")

        except Exception as e:
            logging.warning(f"{TODAY.strftime('%H:%M:%S')}:: DB Error: {e}")

    session.close()


def main(parse_new_data: bool, country: str) -> None:  # noqa:D100
    date_in = TODAY
    off_set = 1000
    date_out = NEXT_DATE
    for i in range(365):
        if parse_new_data:
            get_info(country, off_set, (date_in + datetime.timedelta(i)), date_out)

    remove_extra_rows_by_name()

    draw_map_by_coords('DisplayAllHotels')

    rating = get_hotels_rating()
    schedule_quantity_rating(rating)

    years = get_years_opening_hotels()
    diagram_open_hotels(years)

    spb = 'Санкт-Петербург'
    msk = 'Москва'
    hotels_in_spb = get_hotels_from_city('Санкт-Петербург')
    hotels_in_moscow = get_hotels_from_city('Москва')

    grouped_spb_hotels = group_hotels_by_scores(hotels_in_spb)
    grouped_moscow_hotels = group_hotels_by_scores(hotels_in_moscow)
    pie_chart_from_scores(grouped_moscow_hotels, msk)
    pie_chart_from_scores(grouped_spb_hotels, spb)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--get-data",
                        action='store_true',
                        help='Used to parsing new data from booking.')
    parser.add_argument("--country", "-c",
                        help='Country for parsing.',
                        default='Russia')
    args = parser.parse_args()
    main(args.get_data, args.country)
