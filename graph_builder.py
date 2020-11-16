from collections import Counter  # noqa:D100
from pathlib import Path
from typing import List

import gmplot
import matplotlib.pyplot as plt

from data_base_operation import get_hotels_coordinates

DATA_PATH = Path('Charts')
if not DATA_PATH.exists():
    DATA_PATH.mkdir(exist_ok=True)


def schedule_quantity_rating(rating: List):
    """Build a histogram, where the hotel rating is horizontal, the count is vertical."""
    plt.hist(rating, bins=100, rwidth=0.9, alpha=0.5, label='no', color='r')
    plt.title('Histogram of the number of hotels from their rating')
    plt.ylabel('Count of hotels')
    plt.xlabel('Hotel rating')
    fname = DATA_PATH / 'Number_of_hotels_by_rating'
    plt.savefig(fname)


def diagram_open_hotels(years):
    """Build a histogram of hotel registration on booking.com."""
    years = sorted(years)
    count_year = Counter(years)
    years = []
    counts = []
    for year, count in count_year.items():
        years.append(int(year))
        counts.append(int(count))

    plt.bar(years, counts)
    plt.title('Hotel opening history histogram')
    plt.ylabel('Count of hotels')
    plt.xlabel('Opening year')
    fname = DATA_PATH / 'Number_of_hotels_by_year_of_registration_on_booking'
    plt.savefig(fname)


def draw_map_by_coords(map_name: str) -> None:
    """Draw a map with labels at the given coordinates."""
    coordinates = get_hotels_coordinates()
    gmap = gmplot.GoogleMapPlotter(coordinates[0][1], coordinates[0][2], 5)

    for hotel_coordinate in coordinates:
        hotel_name, latitude, longitude = hotel_coordinate
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except Exception:
            continue
        gmap.marker(latitude, longitude)
    fname = DATA_PATH / 'map_{0}.html'.format(map_name)
    gmap.draw(fname)
