import gmplot  # noqa:D100

from data_base_operation import get_hotels_coordinates


def draw_map_by_coords(map_name: str) -> None:
    """Draw a map with labels at the given coordinates."""
    coordinates = get_hotels_coordinates()
    gmap = gmplot.GoogleMapPlotter(coordinates[0][1], coordinates[0][2], 5)

    for hotel_coordinate in coordinates:
        hotel_name, latitude, longitude = hotel_coordinate
        # if latitude and longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except Exception:
            continue
        gmap.marker(latitude, longitude)

    gmap.draw('map{0}.html'.format(map_name))
