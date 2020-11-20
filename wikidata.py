import logging
from qwikidata.sparql import return_sparql_query_results

def get_city_population_wikidata(city: str) -> int:   
    query = """
    SELECT ?population
    WHERE
    {  
        ?city rdfs:label '%s'@ru.
        ?city wdt:P1082 ?population.
        ?city wdt:P17 ?country.
        ?city rdfs:label ?cityLabel.
        ?country rdfs:label ?countryLabel.
        FILTER(LANG(?cityLabel) = "ru").
        FILTER(LANG(?countryLabel) = "ru").
        FILTER(CONTAINS(?countryLabel, "Россия")).
    }
    ORDER BY DESC(?population)
    LIMIT 1
    """ % (city)
    
    try:
        res = return_sparql_query_results(query)
        population = res['results']['bindings'][0]['population']['value'] or 0
    
        return population
    except Exception as e:
        logging.error(f"Something wrong in getting data from wikidata: {e}")
