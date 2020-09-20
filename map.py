import gmplot

# Получаем координаты для отелей 
def getPositions(hotelsInfo: list):

    hotelsCoordinates = []

    for page in range(len(hotelsInfo)):
        for hotel in range(len(hotelsInfo[page])):
            coords = {
                'latitude': hotelsInfo[page][hotel]['details']['coordinates']['latitude'],
                'longitude': hotelsInfo[page][hotel]['details']['coordinates']['longitude'],
            }
            hotelsCoordinates.append({
                'name': hotelsInfo[page][hotel]['name'],
                'coordinates': coords,
            })

    return hotelsCoordinates

# Пример использования google maps
def drawMapByCoords(coords: list):

    gmap = gmplot.GoogleMapPlotter(coords[0]['coordinates']['latitude'], coords[0]['coordinates']['latitude'], 5)

    for el in coords[:10]:
        ltd = float(el['coordinates']['latitude'])
        lgd = float(el['coordinates']['longitude'])
        gmap.marker(ltd, lgd)

    gmap.draw('map.html')
    # Проверить наличие файла
