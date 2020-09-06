import datetime  # noqa:D100
import requests
from bs4 import BeautifulSoup

session = requests.Session()
REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"}
TODAY = datetime.datetime.now()
NEXT_WEEK = TODAY + datetime.timedelta(7)


def create_link(date_in: datetime.datetime, date_out: datetime.datetime = NEXT_WEEK):
    """Создание ссылки для сбора данных."""
    month = date_in.month
    day = date_in.day
    year = date_in.year
    out_month = date_out.month
    out_day = date_out.day
    out_year = date_out.year
    count_people = 1
    country = "Russia"
    off_set = 1000

    url = "https://www.booking.com/searchresults.ru.html?checkin_month={checkin_month}" \
          "&checkin_monthday={checkin_monthday}" \
          "&checkin_year={checkin_year}" \
          "&checkout_month={checkout_month}" \
          "&checkout_monthday={checkout_monthday}" \
          "&checkout_year={checkout_year}" \
          "&group_adults={group_adults}" \
          "&group_children=0&order=price" \
          "&ss=%2C%20{country}" \
          "&offset={limit}".format(
            checkin_month=month,
            checkin_monthday=day,
            checkin_year=year,
            checkout_month=out_month,
            checkout_monthday=out_day,
            checkout_year=out_year,
            group_adults=count_people,
            country=country,
            limit=off_set
            )
    print("Url created:" + "\n" + "\t" + url)
    return url


def get_info(url: str):
    """Получает данные по ссылке."""
    response = session.get(url, headers=REQUEST_HEADER)
    soup = BeautifulSoup(response.text, "lxml")
    print("Начинаю собирать данные...")
    import pdb; pdb.set_trace()


def main():
    """Главный метод по обработке данных."""
    date_in = TODAY
    print("Введите дату отьезда в формате ##.##.##")
    date_out = input()
    if date_out:
        date_out = datetime.datetime.strptime(date_out, '%d.%m.%y')
        url = create_link(date_in, date_out)
    else:
        url = create_link(date_in)

    get_info(url)


if __name__ == "__main__":
    main()
