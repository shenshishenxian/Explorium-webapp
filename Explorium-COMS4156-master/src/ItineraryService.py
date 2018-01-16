import googlemaps
from TouristSpot import TouristSpot
import json, sqlalchemy
from sqlalchemy import and_
from random import shuffle
import ExploriumDbApi
import urllib

#DISTANCE_MATRIX_API_KEY = 'AIzaSyBLC6wNLVKspJYi-dU9U4HBIYwJOsCKvcc'
DISTANCE_MATRIX_API_KEY = 'AIzaSyBN1B4zPxFFsS3ib69Wcm6mzQ035Q8tCIU'
#GEOCODE_API_KEY = 'AIzaSyB43Kf2f_OCr8QLSCjCDL78yh6u7sA6K_E'
GEOCODE_API_KEY = 'AIzaSyBN1B4zPxFFsS3ib69Wcm6mzQ035Q8tCIU'

POI_LIMIT = 4

DISTANCE_MATRIX_CLIENT = googlemaps.Client(key=DISTANCE_MATRIX_API_KEY)
GEOCODE_CLIENT = googlemaps.Client(key=GEOCODE_API_KEY)


def get_travel_duration(origin, destination):
    duration_element = DISTANCE_MATRIX_CLIENT.distance_matrix(origins=origin, destinations=destination)['rows'][0]['elements'][0]
    if 'duration' in duration_element:
      return duration_element['duration']

def generate_tourist_spot_list(city, preferences=None):
    default_type = ['restaurant', 'museum', 'poi']
    min_price = None
    city_replace = city

    if preferences:
        if 'types' in preferences and preferences['types']:
            types = preferences['types']
        else:
            types = default_type

        max_price = preferences.get('max_price', None)
        if max_price:
            max_price = int(max_price)

        days = int(preferences.get('time_spent', 1))
    else:
        types = default_type
        max_price = None
        days = 1

    # Assume 8 hour days and 2 hours per location
    num_results = int(days)*4
    geocode_result = GEOCODE_CLIENT.geocode(city)
    radius = 50000
    places_list = []
    search = {}
    for typ in types:
        if typ == 'poi':
            city_replace = city_replace.replace(' ', '+').lower()
            myurl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=' + city_replace + '+point+of+interest&language=en&key=' + GEOCODE_API_KEY
            response = urllib.urlopen(myurl).read()
            search = json.loads(response)
        else:
            # search = GEOCODE_CLIENT.places(str(typ.lower()),location=geocode_result[0]['geometry']['location'],
            #                                             radius=radius,
            #                                             min_price = min_price,
            #                                             max_price = max_price,
            #                                             )
            search = GEOCODE_CLIENT.places_nearby(location=geocode_result[0]['geometry']['location'],
                                                  radius=radius,
                                                  max_price = max_price,
                                                  rank_by='prominence',
                                                  type = str(typ.lower()),
                                                  )
        if len(search['results']) > num_results:
            places_list += search['results'][:num_results]
        else:
            places_list += search['results']

    shuffle(places_list)
    if len(places_list) < num_results:
        num_results = len(places_list)
    return places_list[:num_results]

def get_tourist_spot_details(tourist_spot):
    return tourist_spot.to_dict()

#def to_json(places_list):
#    tSpot_list = []
#    for place in places_list:
#        tSpot = TouristSpot(place=place)
#        tSpot_list.append(tSpot.to_dict())
#    tSpot_list = json.dumps(tSpot_list)
#    return tSpot_list



