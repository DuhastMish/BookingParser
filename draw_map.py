from typing import List  # noqa:D100

import gmplot


def get_coords(hotels_info: list) -> List:
    """Получает координаты для отелей."""
    hotels_coordinates = []

    for page in hotels_info:
        for hotel in page:
            hotels_coordinates.append({
                'name': hotel['name'],
                'coordinates': {
                    'latitude': hotel['details']['coordinates']['latitude'],
                    'longitude': hotel['details']['coordinates']['longitude'],
                },
            })

    return hotels_coordinates


def draw_map_by_coords(coords: list, task: str) -> None:
    """Рисует карту с метками по заданным координатам."""
    gmap = gmplot.GoogleMapPlotter(coords[0]['coordinates']['latitude'], coords[0]['coordinates']['latitude'], 5)

    for el in coords:
        ltd = float(el['coordinates']['latitude'])
        lgd = float(el['coordinates']['longitude'])
        gmap.marker(ltd, lgd)

    gmap.draw('map{0}.html'.format(task))
