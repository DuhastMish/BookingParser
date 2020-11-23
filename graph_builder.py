from collections import Counter  # noqa:D100
from pathlib import Path
from typing import List, Dict
from openpyxl import Workbook
from xlsx2html import xlsx2html

import gmplot
import matplotlib.pyplot as plt

from data_base_operation import get_hotels_coordinates
from helper import set_lang_and_table_style

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
    plt.close()


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
    plt.close()


def pie_chart_from_scores(grouped_scores: Dict, city: str) -> None:
    """Draw pie chat of hotels scores."""
    labels = '[1-5)', '[5-8)', '[8-10]'
    amounts_of_scores = [len(grouped_scores['firstGroup']),
                         len(grouped_scores['secondGroup']),
                         len(grouped_scores['thirdGroup'])]
    total = sum(amounts_of_scores)

    fig, ax = plt.subplots()

    colors = ['#FD6787', '#FFF44C', '#288EEB']
    ax.pie(amounts_of_scores, colors=colors, autopct=lambda p: '({:,.0f})'.format(round(p*total/100)),
           wedgeprops={"edgecolor": "0", "linewidth": "1"})

    ax.axis('equal')

    plt.legend(
        loc='upper left',
        labels=['%s, %.2f%%' % (
            label, (score / total) * 100) for label, score in zip(labels, amounts_of_scores)],
        prop={'size': 10},
        bbox_to_anchor=(0.0, 1),
        bbox_transform=fig.transFigure
    )
    plt.title(f'Pie chart with scores for {city}')
    fname = DATA_PATH / f'Pie_chart_with_scores_for_{city}'
    plt.savefig(fname)
    plt.close()


def get_table_of_ratio_data(ratio_data: Dict) -> None:
    """Get table with names of cities, hotels in each city, populations in each city and ratio."""
    wb = Workbook()
    ws = wb.active

    ws['A1'] = 'Город'
    ws['B1'] = 'Кол-во отелей'
    ws['C1'] = 'Население'
    ws['D1'] = 'Соотношение'

    for city_info in zip(ratio_data['cities'], ratio_data['hotels_amounts'],
                         ratio_data['cities_populations'], ratio_data['ratio']):
        city_info = list(city_info)
        ws.append(city_info)

    fname1 = DATA_PATH / 'ratio_data.xlsx'
    wb.save(fname1)

    html_table = xlsx2html(fname1)
    html_table.seek(0)
    html_table = html_table.read()
    fname2 = DATA_PATH / 'ratio_data.html'
    fname2.write_text(html_table)

    set_lang_and_table_style(fname2, "cp1251", "ru", "1", "5", "5",
                             "border: 1px solid black; font-size: 20.0px; height: 19px")


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
