import argparse  # noqa:D100
import datetime
import logging
import re

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from booking_parser import BookingParser
from data_base_operation import get_years_opening_hotels
from data_base_setup import DBEngine
# from draw_map import draw_map_by_coords, get_coords
from graph_builder import diagram_open_hotels

session = requests.Session()
REQUEST_HEADER = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36")}
TODAY = datetime.datetime.now()
NEXT_WEEK = TODAY + datetime.timedelta(1)
BOOKING_PREFIX = 'https://www.booking.com'
DATABASE = DBEngine


def get_max_offset(soup: BeautifulSoup):
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
          "&group_children=0&order=price" \
          "&ss=%2C%20{country}" \
          "&offset={limit}".format(
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


def get_info(country: str, off_set: int, date_in: datetime.datetime, date_out: datetime.datetime):
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
                 date_out: datetime.datetime, off_set: int):
    """Gather information about a specific hotel."""
    data_url = create_link(country, off_set, date_in, date_out)
    response = session.get(data_url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    parser = BookingParser()
    hotels = soup.select("#hotellist_inner div.sr_item.sr_item_new")

    for hotel in tqdm(hotels):
        name = parser.name(hotel)
        rating = parser.rating(hotel)
        price = parser.price(hotel)
        image = parser.image(hotel)
        link = parser.detail_link(hotel)
        city = parser.city(hotel)

        if link is not None:
            detail_page_response = session.get(BOOKING_PREFIX + link, headers=REQUEST_HEADER)
            hotel_html = BeautifulSoup(detail_page_response.text, "lxml")
            latitude = parser.coordinates(hotel_html)[0]
            longitude = parser.coordinates(hotel_html)[1]
            important_facilities = ', '.join(parser.important_facilites(hotel_html))
            neighborhood_structures = parser.neighborhood_structures(hotel_html)
            services_offered = parser.offered_services(hotel_html)
            open_date = parser.open_hotel_date(hotel_html)
            extended_rating = parser.extended_rating(hotel_html)
            reviews = parser.review_rating(hotel_html)
        try:
            with DATABASE.begin() as connection:
                connection.execute(
                    "insert into hotels (name, score, price, image, link, city, open_date) "
                    f"values ('{name}', '{rating}', '{price}', '{image}', '{link}', '{city}', '{open_date}')")
                connection.execute(
                    f"insert into coordinates (latitude, longitude) values ('{latitude}', '{longitude}')")
                connection.execute(
                    f"insert into important_facilities (important_facilities) values ('{important_facilities}')")
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
                        "insert into neighborhood_structures (neighborhood_structure, structure_type, distance) "
                        f"values ('{name}', '{structure_type}', '{distance}')")

                for rating_name, rating_value in extended_rating.items():
                    connection.execute(
                        "insert into extended_rating (hotel_id, rating_name, rating_value) "
                        f"values ('{hotel_id}', '{rating_name}', '{rating_value}')")

                for review_name, review_count in reviews.items():
                    connection.execute(
                        "insert into review_rating (hotel_id, review_rating_name, review_rating_count) "
                        f"values ('{hotel_id}', '{review_name}', '{review_count}')")
        except Exception as e:
            logging.warning(f"{TODAY.strftime('%H:%M:%S')}:: DB Error: {e}")

    session.close()


def main(parse_new_data: bool):
    """The main method for data processing."""
    date_in = TODAY
    country = "Russia"
    off_set = 1000
    date_out = NEXT_WEEK

    if parse_new_data:
        get_info(country, off_set, date_in, date_out)

    # Получаем координаты и рисуем карту
    # coords = get_coords(hotels_info)
    # draw_map_by_coords(coords, 'DisplayAllHotels')
    # schedule_quantity_rating(hotels_info)
    years = get_years_opening_hotels()
    diagram_open_hotels(years)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--get-data",
                        action='store_true',
                        help='Used to parsing new data from booking.')
    args = parser.parse_args()
    main(args.get_data)
