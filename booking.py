import argparse  # noqa:D100
import datetime
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from booking_parser import BookingParser
from draw_map import draw_map_by_coords, get_coords
from graph_builder import schedule_quantity_rating
from data_base_setup import DBEngine


session = requests.Session()
REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
TODAY = datetime.datetime.now()
NEXT_WEEK = TODAY + datetime.timedelta(7)
BOOKING_PREFIX = 'https://www.booking.com'
DATABASE = DBEngine


def get_data_from_json(file_name: Optional[str] = None):
    """Закидование данных с файла в программу."""
    if file_name is None:
        path = Path(__file__).parent
        json_files_path = path.glob('*.json')
        file_name = max((path.stat().st_mtime, path.name) for path in json_files_path)[1]
        # last_changes_time = datetime.datetime.fromtimestamp(last_changes_time)

    with open(file_name, 'r', encoding="utf-8") as f:
        hotel_information = json.load(f)

    return hotel_information


def save_data_to_json(results: List[List[Dict]], country: str) -> None:
    """Запись в файл."""
    date = TODAY.strftime("%Y-%m-%d-%H.%M.%S")
    with open('booking_{country}_{date}.json'.format(country=country, date=date), 'w', encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


def get_max_offset(soup: BeautifulSoup):
    """Получает количество страниц с отелями."""
    all_offset = []
    if soup.find_all('div', {'class': 'sr_header'}) is not None:
        all_offset = soup.find_all('div', {'class': 'sr_header'})[-1].get_text().strip().replace(u'\xa0', '')
        all_offset = round(int(re.search(r'\d+', all_offset).group()) / 25)
    return all_offset


def create_link(country: str, off_set: int, date_in: datetime.datetime, date_out: datetime.datetime) -> str:
    """Создание ссылки для сбора данных."""
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
    """Получает данные по ссылке."""
    url = create_link(country, off_set, date_in, date_out)
    response = session.get(url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    logging.warning(f"{TODAY.strftime('%H:%M:%S')}:: Начинаю собирать данные...")
    hotels_info = []
    off_set = int(get_max_offset(soup))
    offset = 0
    time_for_every_page = []
    if off_set > 0:
        for i in tqdm(range(off_set)):
            start_time = datetime.datetime.now()
            offset += 25
            result = parsing_data(session, country, date_in, date_out, offset)
            hotels_info.append(result)
            save_data_to_json(hotels_info, country)
            end_time = datetime.datetime.now()
            difference = end_time - start_time
            time_for_every_page.append(difference.seconds)

    return hotels_info


def parsing_data(session: requests.Session, country: str, date_in: datetime.datetime,
                 date_out: datetime.datetime, off_set: int):
    """Собирает информацию по конкретному отелю."""

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

        if link is not None:
            detail_page_response = session.get(BOOKING_PREFIX + link, headers=REQUEST_HEADER)
            hotel_html = BeautifulSoup(detail_page_response.text, "lxml")
            latitude = parser.coordinates(hotel_html)[0]
            longitude = parser.coordinates(hotel_html)[1]
            important_facilities = ', '.join(parser.important_facilites(hotel_html))
            #TODO: Придумать добавление в таблицы.
            neighborhood_structures = parser.neighborhood_structures(hotel_html)
            services_offered = parser.offered_services(hotel_html)

        with DATABASE.begin() as connection:
            connection.execute(f"insert into hotels (name, score, price, image, link) values ('{name}', '{rating}', '{price}', '{image}', '{link}')")
            connection.execute(f"insert into coordinates (latitude, longitude) values ('{latitude}', '{longitude}')")
            connection.execute(f"insert into important_facilities (important_facilities) values ('{important_facilities}')")

    session.close()


def main(parse_new_data: bool):
    """Главный метод по обработке данных."""
    date_in = TODAY
    country = "Russia"
    off_set = 1000
    date_out = NEXT_WEEK

    if parse_new_data:
        hotels_info = get_info(country, off_set, date_in, date_out)
        save_data_to_json(hotels_info, country)
    else:
        hotels_info = get_data_from_json()

    # Получаем координаты и рисуем карту
    coords = get_coords(hotels_info)
    draw_map_by_coords(coords, 'DisplayAllHotels')

    schedule_quantity_rating(hotels_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--get-data",
                        action='store_true',
                        help='Used to parsing new data from booking.')
    args = parser.parse_args()
    main(args.get_data)
