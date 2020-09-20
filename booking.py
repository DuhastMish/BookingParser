import datetime  # noqa:D100
import requests
import json
from bs4 import BeautifulSoup

session = requests.Session()
REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
TODAY = datetime.datetime.now()
NEXT_WEEK = TODAY + datetime.timedelta(7)


class Parser:
    def name(hotel):
        if hotel.select_one("span.sr-hotel__name") is None:
            return ''
        else:
            return hotel.select_one("span.sr-hotel__name").text.strip()

    def rating(hotel):
        if hotel.select_one("div.bui-review-score__badge") is None:
            return ''
        else:
            return hotel.select_one("div.bui-review-score__badge").text.strip()

    def price(hotel):
        if hotel.select_one("div.bui-price-display__value.prco-inline-block-maker-helper") is None:
            return ''
        else:
            return hotel.select_one("div.bui-price-display__value.prco-inline-block-maker-helper").text.strip()[
                   :-5].replace(" ", "")


def get_data_from_json():
    """Закидование данных с файла в программу"""
    with open('output.json', 'r', encoding="utf-8") as f:
        hotel_information = json.load(f)

    return hotel_information


def save_data_to_json(results, country):
    """Запись в файл"""
    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d-%H.%M.%S")
    with open('booking_{country}_{date}.json'.format(country=country, date=date), 'w', encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)




def get_max_offset(soup):
    all_offset = []
    if soup.find_all('li', {'class': 'sr_pagination_item'}) is not None:
        all_offset = soup.find_all('li', {'class': 'sr_pagination_item'})[-1].get_text().splitlines()[-1]

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
        limit=off_set
    )

    return url


def get_info(country: str, off_set: int, date_in: datetime.datetime, date_out: datetime.datetime):
    """Получает данные по ссылке."""
    url = create_link(country, off_set, date_in, date_out)
    response = session.get(url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    print("Начинаю собирать данные...")
    hotels_info = []
    off_set = int(get_max_offset(soup))
    offset = 0
    if off_set > 0:
        for i in range(off_set):
            offset += 25
            result = parsing_data(session, country, date_in, date_out, offset)
            hotels_info.append(result)

    return hotels_info


def parsing_data(session, country, date_in, date_out, off_set):
    result = []

    data_url = create_link(country, off_set, date_in, date_out)
    response = session.get(data_url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")

    hotels = soup.select("#hotellist_inner div.sr_item.sr_item_new")

    for hotel in hotels:
        hotel_info = {}
        hotel_info['name'] = Parser.name(hotel)
        hotel_info['rating'] = Parser.rating(hotel)
        hotel_info['price'] = Parser.price(hotel)

        result.append(hotel_info)

    session.close()

    return result


def main():
    """Главный метод по обработке данных."""
    date_in = TODAY
    country = "Russia"
    off_set = 1000
    date_out = NEXT_WEEK

    andrey_govno = get_info(country, off_set, date_in, date_out)
    save_data_to_json(andrey_govno, country)


if __name__ == "__main__":
    main()
