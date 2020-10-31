from typing import Dict, List  # noqa:D100

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
