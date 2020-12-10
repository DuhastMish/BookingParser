import math
from wikidata import get_city_population_wikidata
from data_base_operation import get_hotels_from_city

def group_hotels_by_scores(hotels: list) -> dict:
    grouped_hotels = dict(firstGroup=[], secondGroup=[], thirdGroup=[], fourthGroup=[])

    """firstGroup - [0-7), secondGroup - [7-8), thirdGroup - [8-9), fourthGroup - [9-10]"""
    for hotel in hotels:
        score = float(hotel[1])
        bottom_score = math.floor(score)

        if bottom_score < 7:
            key = 'firstGroup'
        elif bottom_score < 8:
            key = 'secondGroup'
        elif bottom_score < 9:
            key = 'thirdGroup'
        else:
            key = 'fourthGroup'

        grouped_hotels[key].append(score)

    return grouped_hotels

def get_hotels_ratio(cities: list) -> dict:
    hotels_amounts = []
    cities_populations = []
    hotels_to_population_ratio = []

    for city in cities:
        amount = len(get_hotels_from_city(city))
        hotels_amounts.append(amount)

        """The population will be counted in thousands of people"""
        population = round((int(get_city_population_wikidata(city)) / 1000), 4)
        cities_populations.append(population)

        ratio = round((amount / population), 4)
        hotels_to_population_ratio.append(ratio)

    return {'cities': cities,
            'hotels_amounts': hotels_amounts,
            'cities_populations': cities_populations,
            'ratio': hotels_to_population_ratio}
