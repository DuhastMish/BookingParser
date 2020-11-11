from data_base_setup import DBEngine  # noqa:D100
from typing import List, Tuple

DATABASE = DBEngine


def get_years_opening_hotels():
    dates = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute("SELECT open_date FROM hotels")
        dates = open_dates.fetchall()
    return [date[0].split('/')[2] for date in dates]


def get_hotels_coordinates() -> List[Tuple]:
    coordinates = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute(
            "SELECT name, latitude, longitude FROM hotels INNER JOIN coordinates "
            "on hotels.hotel_id == coordinates.hotel_id")
        coordinates = open_dates.fetchall()

    return coordinates


def get_hotels_rating() -> List[float]:
    ratings = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute(
            "SELECT score FROM hotels")
        ratings = open_dates.fetchall()

    return [float(rating[0]) for rating in ratings if rating[0]]
