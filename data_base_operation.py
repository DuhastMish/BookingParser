import logging  # noqa:D100
from typing import List, Tuple

from data_base_setup import DBEngine

DATABASE = DBEngine

TABLE_NAMES = ['hotels', 'coordinates', 'important_facilities',
               'neighborhood_structures', 'services_offered',
               'extended_rating', 'review_rating']


def get_years_opening_hotels():
    """Get hotels registration year in booking.com"""
    dates = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute("SELECT open_date FROM hotels")
        dates = open_dates.fetchall()
    return [date[0].split('/')[2] for date in dates]


def get_hotels_coordinates() -> List[Tuple]:
    """Get the coordination of hotels like (hotel_name, latitude, longitude)."""
    coordinates = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute(
            "SELECT name, latitude, longitude FROM hotels INNER JOIN coordinates "
            "on hotels.hotel_id == coordinates.hotel_id")
        coordinates = open_dates.fetchall()

    return coordinates


def get_hotels_rating() -> List[float]:
    """Get all hotel ratings."""
    ratings = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute(
            "SELECT score FROM hotels")
        ratings = open_dates.fetchall()

    return [float(rating[0]) for rating in ratings if rating[0]]


def remove_extra_rows_by_name() -> None:
    logging.warning("Removing extra rows...")
    with DATABASE.begin() as connection:
        hostels_id = connection.execute(
            "SELECT hotel_id, name "
            "FROM hotels "
            "WHERE hotel_id NOT IN (SELECT MAX(hotel_id) "
            "FROM hotels GROUP BY name);")

        hotels_id = hostels_id.fetchall()
        for hotel_id, name in hotels_id:
            for table in TABLE_NAMES:
                connection.execute(f"DELETE FROM {table} WHERE hotel_id == {hotel_id}")
    logging.warning("Extra rows removed!")