from datetime import datetime  # noqa:D100


def create_link(date_in, date_out):
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

    return url


def main():
    """Главный метод по обработке данных."""
    date_in = datetime.now()
    print("Введите дату отьезда в формате ##.##.##")
    date_out = datetime.strptime(input(), '%d.%m.%y')
    url = create_link(date_in, date_out)
    print(url)


if __name__ == "__main__":
    main()
