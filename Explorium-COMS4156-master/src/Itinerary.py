from RouteOptimizer import Graph, Vertex, Edge
from TouristSpot import TouristSpot
import ItineraryService
from sqlalchemy import and_
import ExploriumDbApi

class Itinerary(object):
    def __init__(self, city, preferences=None, db_id=None, itinerary = None):

        self.city = city
        self.db_id = None
        self.touristSpots = None
        self.days = None
        self.comments = None

        if db_id:
            self.db_id = db_id
            self.touristSpots = ExploriumDbApi.load_itinerary(db_id)
            self.days = len(self.touristSpots)
            self.comments = ExploriumDbApi.get_itinerary_comments(db_id)

        elif itinerary:
            self.touristSpots = []
            for day in itinerary['tourist_spots']:
                day_num = []
                for t_spot in day:
                    day_num.append(TouristSpot(t_spot=t_spot))
                self.touristSpots.append(day_num)
            self.days = len(self.touristSpots)
            self.comments = itinerary.get('comments', None)

        else:
            self.touristSpots = []
            if preferences:
                self.days = preferences.get('time_spent', 1)
            else:
                self.days = 1

            raw_tourist_spots = ItineraryService.generate_tourist_spot_list(city, preferences)
            tourist_spot_list = []

            for spot in raw_tourist_spots:
                ts = TouristSpot(place=spot)

                query = ExploriumDbApi.TOURIST_SPOT_TABLE.select().where(and_(ExploriumDbApi.TOURIST_SPOT_TABLE.c.google_id == ts.destinationID,
                    ExploriumDbApi.TOURIST_SPOT_TABLE.c.name == ts.destinationName))
                result = ExploriumDbApi.conn.execute(query).fetchone()
                if result is None:
                    ts_id = ExploriumDbApi.save_tourist_spot(ts)
                    ts.db_id = ts_id
                else:
                    ts.db_id = result['tourist_spot_id']
                tourist_spot_list.append(ts)
            #print tourist_spot_list
            self.recalibrate_itinerary(tourist_spot_list)

    def recalibrate_itinerary(self, tourist_spot_list):
        for day in range(int(self.days)):
            if len(tourist_spot_list) < 4:
                self.touristSpots.append(tourist_spot_list)
                end_point = len(tourist_spot_list)
            else:
                end_point = (day + 1) * 4
                if end_point > len(tourist_spot_list):
                    end_point = len(tourist_spot_list)
                self.touristSpots.append(tourist_spot_list[day * 4:end_point])
            self.optimize_daily_route(day)
            self.estimate_daily_route_times(day)
            if end_point == len(tourist_spot_list):
                return


    def add_spot(self, ts):
        all_spots = []
        for day in self.touristSpots:
            for t_spot in day:
                all_spots.append(t_spot)
        all_spots.append(ts)
        self.touristSpots = []
        if len(all_spots) % 4 != 0:
            self.days += 1
        self.recalibrate_itinerary(all_spots)

    def del_spot(self, ts):
        all_spots = []
        for day in self.touristSpots:
            for t_spot in day:
                all_spots.append(t_spot)
        self.touristSpots = []
        for i in all_spots:
            if i.destinationID == ts.destinationID:
                all_spots.remove(i)
        if len(all_spots) / 4 < 1 :
            self.days -= 1
        self.recalibrate_itinerary(all_spots)

    def estimate_daily_route_times(self, day):
        for index, spot in enumerate(self.touristSpots[day]):
                if index+1 < len(self.touristSpots[day]):
                    if spot.address and self.touristSpots[day][index+1].address:
                        #print ItineraryService.get_travel_duration(spot.address, self.touristSpots[day][index+1].address)
                        time = ItineraryService.get_travel_duration(spot.address, self.touristSpots[day][index+1].address)
                        if time and 'text' in time:
                            spot.next_dest_time = time['text']

    def optimize_daily_route(self, day):
        graph = Graph()
        order_num = 0
        for spot in self.touristSpots[day]:
            order_num += 1
            v = Vertex(spot)
            graph.vertices[spot.destinationName] = v
         
        for source in graph.vertices:
            for target in graph.vertices:
                if source != target:
                    graph.add_edge(source, target, 1)

        first_stop = self.touristSpots[day][0].destinationName
        new_graph = graph.get_min_spanning_tree(first_stop)
        new_graph.preorder(new_graph.vertices[first_stop])
        self.touristSpots[day] = new_graph.route

    def to_dict(self):
        it_dict = {}
        all_spots = []
        day_num = 0
        for day in self.touristSpots:
            spots = []
            for tourist_spot in day:
                spots.append(tourist_spot.to_dict())
            day_num += 1
            all_spots.append(spots)
        it_dict['tourist_spots'] = all_spots
        it_dict['city'] = self.city
        it_dict['db_id'] = self.db_id

        if self.db_id and not self.comments:
            it_dict['comments'] = ExploriumDbApi.get_itinerary_comments(self.db_id)
        else:
            it_dict['comments'] = self.comments
        return it_dict

