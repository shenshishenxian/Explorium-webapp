class TouristSpot(object):
    def __init__(self, place=None, db_spot=None, t_spot=None):
        if place:
            self.db_id = None
            self.destinationID = place["place_id"]
            self.destinationName = place["name"]
            self.open_time = None
            self.close_time = None
            self.geocode = place["geometry"]["location"]
            image_link = place.get('photos',None)
            if image_link != None:
                self.image_link = image_link[0]['photo_reference']
            else:
                self.image_link = None
            self.introduction = None
            self.rating = place.get("rating",None)

            self.address = place.get("formatted_address", None)
            if not self.address:
                self.address = place.get("vicinity", None)
            self.next_dest_time = None
        
        elif db_spot:
            self.db_id = db_spot['tourist_spot_id']
            self.destinationID = db_spot['google_id']
            self.destinationName = db_spot['name']
            self.open_time = db_spot['open_time']
            self.close_time = db_spot['close_time']

            lat = float(db_spot['latitude'])
            lng = float(db_spot['longitude'])
            self.geocode = {'lat': lat, 'lng': lng}

            self.image_link = db_spot['image_link']
            self.rating = db_spot['rating']
            self.address = db_spot['address']
            self.next_dest_time = None
            self.introduction = None

        elif t_spot:
            self.db_id = None
            self.destinationID = t_spot.get('destinationID', None)
            self.destinationName = t_spot.get('destinationName', None)
            self.open_time = t_spot.get('open_time', None)
            self.close_time = t_spot.get('close_time', None)
            self.geocode = t_spot.get('geocode', None)
            self.image_link = t_spot.get('image_link', None)
            self.rating = t_spot.get('rating', None)
            self.address = t_spot.get('address', None)
            self.next_dest_time = t_spot.get('next_dest_time', None)
            self.introduction = None
        
        else:
            self.db_id = None
            self.destinationID = None
            self.destinationName = None
            self.open_time = None
            self.close_time = None
            self.geocode = None
            self.image_link = None
            self.introduction = None
            self.rating = None
            self.address = None
            self.next_dest_time = None

    def to_dict(self):
        spot = {}
        spot["db_id"] = self.db_id
        spot["destinationID"] = self.destinationID
        spot["destinationName"] = self.destinationName
        spot["open_time"] = self.open_time
        spot["close_time"] = self.close_time
        spot["geocode"] = self.geocode
        spot["image_link"] = self.image_link
        spot["introduction"] = self.introduction
        spot["rating"] = self.rating
        spot["address"] = self.address

        if self.next_dest_time is None:
            spot["next_dest_time"] = ''
        else:
            spot["next_dest_time"] = self.next_dest_time
        return spot