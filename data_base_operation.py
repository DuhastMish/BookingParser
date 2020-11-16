import logging  # noqa:D100
from typing import List, Tuple

from data_base_setup import DBEngine

DATABASE = DBEngine

TABLE_NAMES = ['hotels', 'coordinates', 'important_facilities',
               'neighborhood_structures', 'services_offered',
               'extended_rating', 'review_rating', 'apartaments']


def get_years_opening_hotels():
    """Get hotels registration year in booking.com."""
    dates = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute("SELECT open_date FROM hotels")
        dates = open_dates.fetchall()
    years = []
    
    for date in dates:
        if not date[0]:
            continue
        
        day, month, year = date[0].split('/')
        years.append(year)
    return years


def get_hotels_coordinates() -> List[Tuple]:
    """Get the coordination of hotels like (hotel_name, latitude, longitude)."""
    coordinates = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute(
            "SELECT name, latitude, longitude FROM hotels INNER JOIN coordinates "
            "on hotels.hotel_id == coordinates.hotel_id")
        coordinates = open_dates.fetchall()

    return coordinates


def is_hotel_exist(link: str) -> List:
    """Check if hotel name exists in hotels table."""
    existing = ()
    with DATABASE.begin() as connection:
        hotel_name = connection.execute(f"SELECT EXISTS(SELECT * FROM hotels WHERE link == '{link}')")
        existing = hotel_name.fetchone()

    return True if existing[0] == 1 else False


def get_hotels_rating() -> List[float]:
    """Get all hotel ratings."""
    ratings = []
    with DATABASE.begin() as connection:
        open_dates = connection.execute(
            "SELECT score FROM hotels")
        ratings = open_dates.fetchall()

    return [float(rating[0]) for rating in ratings if rating[0]]

def get_hotels_from_city(city: str) -> List:
    """Get all hotels, which location is in the folowing city"""
    with DATABASE.begin() as connection:
        result = connection.execute(f"SELECT name, score, city FROM hotels WHERE city like '%{city}%' AND score != ''")
        hotels_info = result.fetchall()
    
    return hotels_info    

def remove_extra_rows_by_name() -> None:
    """Remove existing rows from all tables by name."""
    with DATABASE.begin() as connection:
        hostels_id = connection.execute(
            "SELECT hotel_id, name "
            "FROM hotels "
            "WHERE hotel_id NOT IN (SELECT MIN(hotel_id) "
            "FROM hotels GROUP BY name);")

        hotels_id = hostels_id.fetchall()
        for hotel_id, name in hotels_id:
            for table in TABLE_NAMES:
                connection.execute(f"DELETE FROM {table} WHERE hotel_id == {hotel_id}")
    logging.warning(f": {len(hotels_id)} Extra rows removed!")
