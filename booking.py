

def create_link():
    """Создание ссылки для сбора данных."""
    month = "09"
    day = "15"
    year = "2020"
    out_month="09"
    out_day = "17"
    out_year = "2020"
    count_people = "1"
    city = "Kazan"
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
          "&ss={city}%2C%20{country}" \
          "&offset={limit}".format(
            checkin_month=month,
            checkin_monthday=day,
            checkin_year=year,
            checkout_month=out_month,
            checkout_monthday=out_day,
            checkout_year=out_year,
            group_adults=count_people,
            city=city,
            country=country,
            limit=off_set
            )

    return url


def main():
    url = create_link()
    print(url)


if __name__ == "__main__":
    main()