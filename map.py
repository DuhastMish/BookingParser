import gmplot
import datetime

# Получаем координаты для отелей 
def get_coords(hotels_info: list):

    hotels_coordinates = []

    for page in range(len(hotels_info)):
        for hotel in range(len(hotels_info[page])):
            coords = {
                'latitude': hotels_info[page][hotel]['details']['coordinates']['latitude'],
                'longitude': hotels_info[page][hotel]['details']['coordinates']['longitude'],
            }
            hotels_coordinates.append({
                'name': hotels_info[page][hotel]['name'],
                'coordinates': coords,
            })

    return hotels_coordinates

# Пример использования google maps
def draw_map_by_coords(coords: list, task: str):

    gmap = gmplot.GoogleMapPlotter(coords[0]['coordinates']['latitude'], coords[0]['coordinates']['latitude'], 5)

    for el in coords[:10]:
        ltd = float(el['coordinates']['latitude'])
        lgd = float(el['coordinates']['longitude'])
        gmap.marker(ltd, lgd)

    gmap.draw('map{0}.html'.format(task))
