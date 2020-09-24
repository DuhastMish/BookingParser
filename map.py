import gmplot
from typing import List

def get_coords(hotels_info: list) -> list:
    # Получаем координаты для отелей 

    hotels_coordinates = []

    for page in range(len(hotels_info)):
        for hotel in range(len(hotels_info[page])):
            hotels_coordinates.append({
                'name': hotels_info[page][hotel]['name'],
                'coordinates': {
                    'latitude': hotels_info[page][hotel]['details']['coordinates']['latitude'],
                    'longitude': hotels_info[page][hotel]['details']['coordinates']['longitude'],
                },
            })

    return hotels_coordinates

def draw_map_by_coords(coords: list, task: str) -> None:
    # Рисует карту с метками по заданным координатам

    gmap = gmplot.GoogleMapPlotter(coords[0]['coordinates']['latitude'], coords[0]['coordinates']['latitude'], 5)
    
    for el in coords:
        ltd = float(el['coordinates']['latitude'])
        lgd = float(el['coordinates']['longitude'])
        gmap.marker(ltd, lgd)

    gmap.draw('map{0}.html'.format(task))
