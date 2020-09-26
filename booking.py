import datetime  # noqa:D100
import requests
import json
import re
import logging
from bs4 import BeautifulSoup
from typing import List, Dict
from map import get_coords, draw_map_by_coords
from collections import Counter
import matplotlib.pyplot as plt

session = requests.Session()
REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
TODAY = datetime.datetime.now()
NEXT_WEEK = TODAY + datetime.timedelta(7)
BOOKING_PREFIX = 'https://www.booking.com'


class Parser:
    def name(self, hotel):
        """Возвращает имя отеля."""
        if hotel.select_one("span.sr-hotel__name") is None:
            return ''
        else:
            return hotel.select_one("span.sr-hotel__name").text.strip()

    def rating(self, hotel):
        """Возвращает рейтинг отеля."""
        if hotel.select_one("div.bui-review-score__badge") is None:
            return ''
        else:
            return hotel.select_one("div.bui-review-score__badge").text.strip()

    def price(self, hotel):
        """Возвращает даты на выбранные период времени."""
        if hotel.select_one("div.bui-price-display__value.prco-inline-block-maker-helper") is None:
            return ''
        else:
            return hotel.select_one("div.bui-price-display__value.prco-inline-block-maker-helper"
                                    ).text.strip()[:-5].replace(" ", "")

    def detail_link(self, hotel):
        """Возвращает ссылку на отель."""
        if hotel.select_one(".txp-cta.bui-button.bui-button--primary.sr_cta_button") is None:
            return ''
        else:
            return hotel.select_one(".txp-cta.bui-button.bui-button--primary.sr_cta_button")['href']

    def image(self, hotel):
        """Возвращает ссылку на изображение отеля."""
        if hotel.select_one("img.hotel_image") is None:
            return ''
        else:
            return hotel.select_one("img.hotel_image")['src']

    def coordinates(self, soup):
        """Получает координаты отеля."""
        coordinates = []
        if soup.select_one("#hotel_sidebar_static_map") is None:
            coordinates.append('')
            coordinates.append('')
        else:
            coordinates.append(soup.select_one(
                "#hotel_sidebar_static_map")["data-atlas-latlng"].split(",")[0])
            coordinates.append(soup.select_one(
                "#hotel_sidebar_static_map")["data-atlas-latlng"].split(",")[1])

        return coordinates

    def important_facilites(self, soup):
        """Возвращает важные услуги."""
        if soup.select_one(
                "div.hp_desc_important_facilities.clearfix.hp_desc_important_facilities--bui") is None:
            return []
        else:
            return list(dict.fromkeys([service.text.strip() for service in soup.findAll(
                "div", {"class": "important_facility"})]))

    def offered_services(self, soup):
        """Возвращает предлагаемые услуги отелем."""
        services_offered_list = []

        if soup.select_one('div.facilitiesChecklist') is None:
            services_offered_list = []
        else:

            for services in soup.findAll("div", class_="facilitiesChecklistSection"):

                services_offered = {}
                services_offered['type'] = services.find("h5").text.strip()

                services_offered['value'] = []
                for checks in services.findAll("li"):

                    if checks.find("p") is not None:
                        services_offered['value'].append(
                            checks.findNext(
                                "p").text.strip().replace("\n", " ").replace("\r", " ").replace("  ", " "))

                    elif checks.find("span") is not None:
                        services_offered['value'].append(checks.find("span").text.strip())
                    else:
                        services_offered['value'].append(checks.text.strip())

                services_offered_list.append(services_offered)

        return services_offered_list

    def neighborhood_structures(self, soup):
        """Возвращает ближайщие достопримечательности."""
        neighborhood_list = []

        if soup.select_one('div.hp-poi-content-container.hp-poi-content-container--column.clearfix') is None:
            neighborhood_list = []
        else:
            for neighborhood in soup.select_one(
                    'div.hp-poi-content-container.hp-poi-content-container--column.clearfix').findAll('li', {
                "class": "bui-list__item"}):
                neighborhood_structures = {}

                if neighborhood.find("div", {"class": "hp-poi-list__description"}).contents[0].strip() == '':
                    neighborhood_structures['name'] = neighborhood.find("div", {
                        "class": "hp-poi-list__description"}).span.text.strip()
                else:
                    neighborhood_structures['name'] = \
                    neighborhood.find("div", {"class": "hp-poi-list__description"}).contents[0].strip()

                try:
                    neighborhood_structures['structure_type'] = neighborhood.find("div", {
                        "class": "hp-poi-list__body"}).select_one("span.bui-badge.bui-badge--outline").text.strip()
                except:
                    neighborhood_structures['structure_type'] = ''

                try:
                    neighborhood_structures['distance'] = neighborhood.find('span', {
                        "class": "hp-poi-list__distance"}).text.strip()
                except:
                    neighborhood_structures['distance'] = ''

                neighborhood_list.append(neighborhood_structures)

        return neighborhood_list


def get_data_from_json(file_name: str):
    """Закидование данных с файла в программу."""
    with open(file_name, 'r', encoding="utf-8") as f:
        hotel_information = json.load(f)

    return hotel_information


def save_data_to_json(results: List[List[Dict]], country: str):
    """Запись в файл."""
    date = TODAY.strftime("%Y-%m-%d-%H.%M.%S")
    with open('booking_{country}_{date}.json'.format(country=country, date=date), 'w', encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


def get_max_offset(soup):
    """Получает количество страниц с отелями."""
    all_offset = []
    if soup.find_all('div', {'class': 'sr_header'}) is not None:
        all_offset = soup.find_all('div', {'class': 'sr_header'})[-1].get_text().strip().replace(u'\xa0', '')
        all_offset = round(int(re.search(r'\d+', all_offset).group()) / 25)
    return all_offset


def create_link(country: str, off_set: int, date_in: datetime.datetime, date_out: datetime.datetime):
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
        for i in range(off_set):
            start_time = datetime.datetime.now()
            offset += 25
            result = parsing_data(session, country, date_in, date_out, offset)
            hotels_info.append(result)
            save_data_to_json(hotels_info, country)
            end_time = datetime.datetime.now()
            difference = end_time - start_time
            time_for_every_page.append(difference.seconds)
            logging.warning(f"Страница {i + 1} из {off_set} собрана")
            logging.warning(
                f"Время до конца {(sum(time_for_every_page) / len(time_for_every_page)) * (off_set - i) / 3600} часов")
    return hotels_info


def parsing_data(session: requests.Session, country: str, date_in: datetime.datetime,
                 date_out: datetime.datetime, off_set: int):
    """Собирает информацию по конкретному отелю."""
    result = []

    data_url = create_link(country, off_set, date_in, date_out)
    response = session.get(data_url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    parser = Parser()
    hotels = soup.select("#hotellist_inner div.sr_item.sr_item_new")

    for hotel in hotels:
        hotel_info = {}
        hotel_info['name'] = parser.name(hotel)
        hotel_info['rating'] = parser.rating(hotel)
        hotel_info['price'] = parser.price(hotel)
        hotel_info['image'] = parser.image(hotel)
        hotel_info['link'] = parser.detail_link(hotel)
        if hotel_info['link'] is not None:
            detail_page_response = session.get(BOOKING_PREFIX + hotel_info['link'], headers=REQUEST_HEADER)
            hotel_html = BeautifulSoup(detail_page_response.text, "lxml")
            additional_info = {}
            additional_info['coordinates'] = {}
            additional_info['coordinates']['latitude'] = parser.coordinates(hotel_html)[0]
            additional_info['coordinates']['longitude'] = parser.coordinates(hotel_html)[1]
            additional_info['important_facilities'] = parser.important_facilites(hotel_html)
            additional_info['neighborhood_structures'] = parser.neighborhood_structures(hotel_html)
            additional_info['services_offered'] = parser.offered_services(hotel_html)
            hotel_info['details'] = additional_info

        logging.warning(f"Данные для отеля {hotel_info['name']} получены")

        result.append(hotel_info)

    session.close()

    return result


def schedule_quantity_rating(results: List[List[Dict]]):
    rating = []
    for page in results:
        for hotel in page:
            rating.append(hotel['rating'])
    c = Counter(rating)
    c = sorted(c.items())
    print(c)
    plt.hist(rating, bins=20, rwidth=0.9, alpha=0.5, label='no', color='r')
    plt.title('Histogram of the number of hotels from their rating')
    plt.ylabel('Count of hotels')
    plt.xlabel('Hotel rating')
    plt.show()

    print(c)


def main():
    """Главный метод по обработке данных."""
    date_in = TODAY
    country = "Russia"
    off_set = 1000
    date_out = NEXT_WEEK

    # hotels_info = get_info(country, off_set, date_in, date_out)

    # save_data_to_json(hotels_info, country)

    hotels_file_name = 'booking_Russia_2020-09-25-18.37.26.json'
    hotels_info = get_data_from_json(hotels_file_name)
    # Получаем координаты и рисуем карту
    coords = get_coords(hotels_info)
    draw_map_by_coords(coords, 'FirstTenNumbers')

    schedule_quantity_rating(hotels_info)


if __name__ == "__main__":
    main()
