from typing import Dict, List  # noqa:D100
from collections import Counter

import matplotlib.pyplot as plt


def schedule_quantity_rating(results: List[List[Dict]]):
    rating = []
    for page in results:
        for hotel in page:
            if hotel['rating'] != '':
                rating.append(float(hotel['rating'].replace(',', '.')))
            else:
                continue

    plt.hist(rating, bins=100, rwidth=0.9, alpha=0.5, label='no', color='r')
    plt.title('Histogram of the number of hotels from their rating')
    plt.ylabel('Count of hotels')
    plt.xlabel('Hotel rating')
    plt.show()

def diagramma_open_hotels(years):
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
    plt.show()
    