import math

def group_hotels_by_scores(hotels: list):
    grouped_hotels = dict(firstGroup=[], secondGroup=[], thirdGroup=[])
    
    """firstGroup - [1-5), secondGroup - [5-8), thirdGroup - [8-10]"""
    for hotel in hotels:
        score = float(hotel[1])
        bottom_score = math.floor(score)
        
        if bottom_score < 5:
            key = 'firstGroup'
        elif bottom_score < 8:
            key = 'secondGroup'
        else:
            key = 'thirdGroup'
        
        grouped_hotels[key].append(score)
    
    return grouped_hotels