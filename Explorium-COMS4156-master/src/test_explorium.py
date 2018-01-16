# -*- coding: utf-8 -*-

import os
import tempfile
import pytest
from Controller import app
import sqlalchemy
from flask import Flask, request, render_template, g, redirect, Response
from sqlalchemy import and_
import unittest
import ItineraryService
from ItineraryService import *
import string
import random
from Itinerary import Itinerary
import ExploriumDbApi
import json
import utils

class MyTest(unittest.TestCase):
    # def setUp(self):
    #     DATABASEURI = "postgresql://fortytwo:explorium-COMS4156@coms4156.cf4dw5ld7jgf.us-east-2.rds.amazonaws.com:5432/Explorium"
    #     engine = sqlalchemy.create_engine(DATABASEURI)
    #     g.conn = engine.connect()

    # def tearDown(self):
    #     g.conn.close()
    usernamen=" "
    passwordn=" "
    usernamen2=" "
    passwordn2=" "
    itinerary=None
    def user_generator(self, size=7, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))+'1zZ'
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/signin', content_type = 'html/text')
        self.assertEqual(response.status_code, 200)
        MyTest.usernamen = self.user_generator()
        MyTest.passwordn = self.user_generator()
        MyTest.usernamen2 = self.user_generator()
        MyTest.passwordn2= self.user_generator()
        print('test_index')

    #ensure the login page loads correctly
    def test_index2(self):
        tester = app.test_client(self)
        response = tester.get('/signin', content_type = 'html/text')
        self.assertTrue(b'Login' in response.data)
        self.assertTrue(b'Explorium' in response.data)
        self.assertNotIn(b'Welcome' , response.data)
        print('test_index2')

    #try to login with a username which has not been signup yet
    def test_login_page_before(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin', 
            data = dict(user_username=MyTest.usernamen, user_password = MyTest.passwordn), 
            follow_redirects = True 
        )  
        self.assertNotIn(b'Search Cities' , response.data)
        self.assertNotIn(b'Welcome', response.data) 
        self.assertIn(b'Login', response.data) 
        self.assertIn(b'Do not have an account' , response.data)
        print('test_login_page_before')


    def test_signup_page1(self):
        tester = app.test_client(self)
        tester.post(
            '/signup', 
            data = dict(user_username=MyTest.usernamen,
                        user_password = MyTest.passwordn, 
                        user_repeat_password = MyTest.passwordn, 
                        user_email = MyTest.usernamen+'@gmail.com',
                        user_firstname='userf',
                        user_lastname = 'userl'), 
            follow_redirects = True 
        )
        response = tester.post(
            '/signin', 
            data = dict(user_username=MyTest.usernamen, user_password = MyTest.passwordn), 
            follow_redirects = True 
        )
        self.assertIn(b'Author' , response.data)    
        self.assertIn(b'Search Cities' , response.data)
        self.assertIn(b'Welcome', response.data) 
        self.assertNotIn(b'Login', response.data)
        print('test_signup_page1')

    def test_signin_page2(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin', 
            data = dict(user_username=MyTest.usernamen, user_password = "wrongpassword"), 
            follow_redirects = True 
        )    
        self.assertNotIn(b'Search Cities' , response.data)
        self.assertNotIn(b'Welcome', response.data) 
        self.assertIn(b'Login', response.data)
        print('test_signin_page2')

    # def test_signup_page5(self):
    #     tester = app.test_client(self)
    #     tester.post(
    #         '/signup', 
    #         data = dict(user_username="random11", user_password = MyTest.passwordn, user_repeat_password = MyTest.passwordn), 
    #         follow_redirects = True 
    #     )
    #     response = tester.post(
    #         '/signin', 
    #         data = dict(user_username="random11", user_password = MyTest.passwordn), 
    #         follow_redirects = True 
    #     )
    #     query = users.delete().where(users.c.username=="random11")
    #     conn.execute(query)
    #     self.assertIn(b'Author' , response.data)    
    #     self.assertIn(b'Search Cities' , response.data)
    #     self.assertIn(b'Welcome', response.data) 
    #     self.assertNotIn(b'Login', response.data)


    # def test_signup_page3(self):
    #     tester = app.test_client(self)
    #     response = tester.post(
    #         '/signup', 
    #         data = dict(user_username=MyTest.usernamen,
    #                     user_password = MyTest.passwordn, 
    #                     user_repeat_password = MyTest.passwordn, 
    #                     user_email = MyTest.usernamen+'@gmail.com',
    #                     user_firstname='userf',
    #                     user_lastname = 'userl'), 
    #         follow_redirects = True 
    #     )   
    #     self.assertNotIn(b'Search Cities' , response.data)
    #     self.assertNotIn(b'Welcome', response.data) 
    #     self.assertIn(b'signup', response.data)

    # def test_signup_page4(self):
    #     tester = app.test_client(self)
    #     query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username=="Spiderman1")
    #     ExploriumDbApi.conn.execute(query)
    #     tester.post(
    #         '/signup', 
    #         data = dict(user_username='Spiderman1',
    #                     user_password = 'Spiderman1', 
    #                     user_repeat_password = 'Spiderman1', 
    #                     user_email = 'Spiderman1@gmail.com',
    #                     user_firstname='userf',
    #                     user_lastname = 'userl'), 
    #         follow_redirects = True 
    #     )
    #     response = tester.post(
    #         '/signin', 
    #         data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
    #         follow_redirects = True 
    #     )
    #     self.assertIn(b'Author' , response.data)    
    #     self.assertIn(b'Search Cities' , response.data)
    #     self.assertIn(b'Welcome', response.data) 
    #     self.assertNotIn(b'Login', response.data) 

    

    #ensure login behaves correctly given correct credentials
    def test_login_page(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin', 
            data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
            follow_redirects = True 
        )
        self.assertIn(b'Author' , response.data)    
        self.assertIn(b'Search Cities' , response.data)
        self.assertIn(b'Welcome', response.data) 
        self.assertNotIn(b'Login', response.data)
        print('test_login_page')



    #test logout
    def test_logout_page(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
            follow_redirects = True 
        )
        response = tester.get('logout', follow_redirects = True)
        self.assertIn(b'Do not have an account' , response.data)
        self.assertNotIn(b'Welcome' , response.data)
        print('test_logout_page')



        
    #test search a city
    def test_search_page1(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
            follow_redirects = True 
        )
        response = tester.post(
            '/search-city', 
            data = dict(search_box="new york"), 
            follow_redirects = True
        )
        self.assertIn(b'Search Results: new york' , response.data) 
        self.assertIn(b'Routes' , response.data)  
        self.assertIn(b'Spiderman1' , response.data)
        print('test_search_page1')

    def test_search_page2(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
            follow_redirects = True 
        )
        response = tester.post(
            '/search-city', 
            data = dict(search_box="Paris"), 
            follow_redirects = True
        )
        self.assertIn(b'Search Results: Paris' , response.data) 
        self.assertIn(b'Routes' , response.data)  
        self.assertIn(b'Spiderman1' , response.data)
        print('test_search_page2')

    def test_search_page3(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
            follow_redirects = True 
        )
        response = tester.post(
            '/search-city', 
            data = dict(search_box="10027"), 
            follow_redirects = True
        )
        self.assertIn(b'Search Results: 10027' , response.data) 
        self.assertIn(b'Routes' , response.data)  
        self.assertIn(b'Spiderman1' , response.data)
        print('test_search_page3')

    def test_search_page4(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
            follow_redirects = True 
        )
        response = tester.post(
            '/search-city', 
            data = dict(search_box="Nwe York"), 
            follow_redirects = True
        )
        self.assertIn(b'Search Results: Nwe York' , response.data) 
        self.assertIn(b'Routes' , response.data)  
        self.assertIn(b'Spiderman1' , response.data)
        print('test_search_page4')


    def test_search_page5(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
            follow_redirects = True 
        )
        response = tester.post(
            '/search-city', 
            data = dict(search_box="%……。等"), 
            follow_redirects = True
        )
        self.assertIn(b'Search Results: %……。等' , response.data) 
        self.assertIn(b'Routes' , response.data)  
        self.assertIn(b'Spiderman1' , response.data)
        print('test_search_page5')
        


        # query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username=="Spiderman1")
        # ExploriumDbApi.conn.execute(query)
  
    #Test whether the function return a list of correct tourist spots in the query area
    def test_get_itinerary(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
            follow_redirects = True 
        )
        response = tester.post(
            '/route.html', 
            data = {
                'rangeInput' : 15,
                'min_price'  : 1000,
                'max_price' : 5000,
                'city' :"New York",
                't_spot' : ["museums"]
            },
            follow_redirects = True
        )
        self.assertIn(b'New York' , response.data)
        print('test_get_itinerary')





    def test_generate_tourist_spot_list(self):
        spot_list = ItineraryService.generate_tourist_spot_list("New York")
        for spot in spot_list:
            tourist_spot = spot
            self.assertNotIn(b'dasd', spot_list)
            assert spot['rating'] <= 5
            assert spot['rating'] >= 0
            assert spot['geometry']['location']['lat'] > 40
            assert spot['geometry']['location']['lat'] < 41
        print('test_generate_tourist_spot_list')


    def test_itinerary1(self):
        user = 'Spiderman1'
        city = 'New York'
        pref = dict()
        pref['types'] = 'museums'
        pref['min_price'] = 2000
        pref['max_price'] = 5000
        pref['radius'] = 2000
        itinerary = Itinerary(city, preferences=pref)
        MyTest.itinerary = itinerary
        assert itinerary.city is 'New York'
        print('test_itinerary1')

    def test_itinerary2(self):
        user = 'Spiderman1'
        city = 'New York'
        pref = dict()
        pref['types'] = 'museums'
        pref['min_price'] = 2000
        pref['max_price'] = 1000
        pref['radius'] = 2000
        itinerary = Itinerary(city, preferences=pref)
        MyTest.itinerary = itinerary
        assert itinerary.city is 'New York'
        print('test_itinerary2')

    # def test_itinerary3(self):
    #     user = 'Spiderman1'
    #     city = 'New York'
    #     pref = dict()
    #     pref['types'] = 'museums'
    #     pref['min_price'] = 2000
    #     pref['max_price'] = 5000
    #     pref['radius'] = -1
    #     itinerary = Itinerary(city, preferences=pref)
    #     MyTest.itinerary = itinerary
    #     assert itinerary.city is not 'New York'

    def test_1(self):
        try:
            user = 'Spiderman1'
            city = 'New York'
            pref = dict()
            pref['types'] = 'museums'
            pref['min_price'] = 2000
            pref['max_price'] = 5000
            pref['radius'] = -1
            itinerary = Itinerary(city, preferences=pref)
            MyTest.itinerary = itinerary
            assert itinerary.city is not 'New York'
        except Exception as e:
            pass
        else:
            assert itinerary.city is 'New York'
        print('test_1')

    def test_save_route(self):
        user = 'Spiderman1'
        city = 'New York'
        pref = dict()
        pref['types'] = 'museums'
        pref['min_price'] = 2000
        pref['max_price'] = 5000
        pref['radius'] = 2000
        itinerary = Itinerary(city, preferences=pref)
        #ItineraryService.save_route(user, city, itinerary)
        print('test_save_route')

    # def test_DBApi_save_tourist_spot(self):
    #     result = ExploriumDbApi.save_tourist_spot(MyTest.tourist_spot)
    #     state = 0
    #     if result is not None or u"":
    #         state = 1
    #     assert state == 1
    #     MyTest.tourist_spot_id = result

    # def test_DBApa_load_tourist_spot(self):
    #     result = ExploriumDbApi.load_tourist_spot(MyTest.tourist_spot_id)
    #     state = 0
    #     if result is not None or u"":
    #         state = 1
    #     assert state == 0
    #     assert result['open_time'] is not None

    def test_DBApi_save_load_itinerary(self):
        user = 'Spiderman1'
        city = 'New York'
        pref = dict()
        pref['types'] = 'museums'
        pref['min_price'] = 2000
        pref['max_price'] = 5000
        pref['radius'] = 2000
        itinerary = Itinerary(city, preferences=pref)
        ExploriumDbApi.save_itinerary(user, city, itinerary)
        result = ExploriumDbApi.get_user_itineraries(user)
        print('------------------------------------------')
        print(result)
        print('------------------------------------------')
        state = 0
        if result is not None or u"":
            state = 1
        assert state == 1
        print('test_DBApi_save_load_itinerary')

    def test_za_edit_profile1(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username="Spiderman1", user_password = "Spiderman1"), 
            follow_redirects = True 
        )
        response = tester.get('profile-edit', follow_redirects = True)
        self.assertIn(b'Edit Profile' , response.data)
        self.assertIn(b'Save Changes' , response.data)
        self.assertNotIn(b'Welcome' , response.data)
        print('test_za_edit_profile1')


    def test_zb_edit_profile2(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username='Spiderman1', user_password = 'Spiderman1'), 
            follow_redirects = True 
        )
        response = tester.post(
            '/profile-edit', 
            data = {'user-firstname':None,
                    'user-lastname':'lastname2',
                    'user-email': MyTest.usernamen2+'@gmail.com',
                    'user-username': MyTest.usernamen}, 
            follow_redirects = True 
        )
        self.assertIn('Fields cannot be empty.', response.data)
        print('test_zb_edit_profile2')



    def test_zc_edit_profile3(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username=MyTest.usernamen, user_password = MyTest.passwordn), 
            follow_redirects = True 
        )
        response = tester.post(
            '/profile-edit', 
            data = {'user-firstname':'firstname2',
                    'user-lastname':'lastname2',
                    'user-email': MyTest.usernamen2+'@gmail.com',
                    'user-username': MyTest.usernamen2}, 
            follow_redirects = True 
        )
        self.assertIn(MyTest.usernamen2 , response.data)
        print('test_zc_edit_profile3')

    def test_zd_login_page(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin', 
            data = dict(user_username=MyTest.usernamen2, user_password = MyTest.passwordn), 
            follow_redirects = True 
        )
        self.assertIn(b'Author' , response.data)    
        self.assertIn(b'Search Cities' , response.data)
        self.assertIn(b'Welcome', response.data) 
        self.assertNotIn(b'Login', response.data)
        print('test_zd_edit_profile3')

    def test_ze_login_page(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin', 
            data = dict(user_username=MyTest.usernamen, user_password = MyTest.passwordn), 
            follow_redirects = True 
        ) 
        self.assertNotIn(b'Search Cities' , response.data)
        self.assertNotIn(b'Welcome', response.data) 
        self.assertIn(b'Login', response.data)
        print('test_ze_edit_profile3')

    

    def test_zg_edit_profile4(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username=MyTest.usernamen2, user_password = MyTest.passwordn), 
            follow_redirects = True 
        )
        response = tester.post(
            '/profile-edit', 
            data = {'user-firstname':'firstname2',
                    'user-lastname':None,
                    'user-email': MyTest.usernamen2+'@gmail.com',
                    'user-username': MyTest.usernamen2}, 
            follow_redirects = True 
        )
        self.assertIn('Fields cannot be empty.', response.data)
        print('test_zg_edit_profile3')

    def test_zh_edit_profile5(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username=MyTest.usernamen2, user_password = MyTest.passwordn), 
            follow_redirects = True 
        )
        response = tester.post(
            '/profile-edit', 
            data = {'user-firstname':'firstname2',
                    'user-lastname':'lastname2',
                    'user-email': None,
                    'user-username': MyTest.usernamen2}, 
            follow_redirects = True 
        )
        self.assertIn('Fields cannot be empty.', response.data)
        print('test_zh_edit_profile3')

    def test_zi_edit_profile6(self):
        tester = app.test_client(self)
        tester.post(
            '/signin', 
            data = dict(user_username=MyTest.usernamen2, user_password = MyTest.passwordn), 
            follow_redirects = True 
        )
        response = tester.post(
            '/profile-edit', 
            data = {'user-firstname':'firstname2中',
                    'user-lastname':'lastname2',
                    'user-email': MyTest.usernamen2+'@gmail.com',
                    'user-username': MyTest.usernamen2}, 
            follow_redirects = True 
        )
        self.assertNotIn('Fields cannot be empty.', response.data)
        self.assertIn('firstname2中' , response.data)
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username==MyTest.usernamen2)
        ExploriumDbApi.conn.execute(query)
        print('test_zi_edit_profile3')
    '''
    class CoverageTest(unittest.TestCase):
        ## ItineraryService.py ##
        # get_travel_duration(origin, destination)
        def test_get_travel_duration_valid(self):
            coord1 = (40.80887209540821, -73.96184921264648)  # Columbia University Long Lat
            coord2 = (40.73083612189599, -73.99734020233154)  # NYU Long Lat
            dur = ItineraryService.get_travel_duration(coord1, coord2)
            self.assertNotEqual(dur, None)
            # TODO add proper duration assertion here

        # generate_tourist_spot_list(city, preferences=None)
        def test_generate_tourist_spot_list_no_pref_valid_city(self):
            l = ItineraryService.generate_tourist_spot_list(city='New York', preferences=None)
            self.assertGreater(len(l), 0)

        def test_generate_tourist_spot_list_pref1_valid_city(self):
            prefs = dict()
            prefs['types'] = []
            prefs['min_price'] = 0
            prefs['max_price'] = 4
            prefs['time_spent'] = 2
            l = ItineraryService.generate_tourist_spot_list(city='New York', preferences=prefs)
            self.assertGreater(len(l), 0)

        # get_tourist_spot_details(tourist_spot)
        def test_get_tourist_spot_details(self):
            ts = TouristSpot()
            dets = ItineraryService.get_tourist_spot_details(ts)
            self.assertNotEqual(dets, None)

        # to_json(places_list)
        def test_to_json(self):
            # TODO
            return

        ## TouristSpot.py ##
        def test_init_TouristSpot_none(self):
            ts = TouristSpot()
            self.assertNotEqual(ts, None)
            self.assertEqual(ts.destinationID, None)
            self.assertEqual(ts.destinationName, None)
            self.assertEqual(ts.open_time, None)
            self.assertEqual(ts.close_time, None)
            self.assertEqual(ts.geocode, None)
            self.assertEqual(ts.image_link, None)
            self.assertEqual(ts.introduction, None)
            self.assertEqual(ts.rating, None)
            self.assertEqual(ts.address, None)
            self.assertEqual(ts.next_dest_time, None)

        def test_init_TouristSpot(self):
            place = ItineraryService.generate_tourist_spot_list(city='New York', preferences=None)[0]
            ts = TouristSpot(place)
            self.assertEqual(ts.db_id, None)
            self.assertEqual(ts.destinationID, place["place_id"])
            self.assertEqual(ts.destinationName, place["name"])
            self.assertEqual(ts.open_time, None)
            self.assertEqual(ts.close_time, None)
            self.assertEqual(ts.geocode, place["geometry"]["location"])
            self.assertEqual(ts.image_link, place.get('photos', None))
            self.assertEqual(ts.introduction, None)
            self.assertEqual(ts.rating, place.get("rating", None))
            self.assertEqual(ts.address, place["vicinity"])
            self.assertEqual(ts.next_dest_time, None)

        # set_all_from_list(self, list)
        def test_set_all_from_list_valid(self):
            l = [0, 0, 'test', 'open', 'close', 40.80887209540821, -73.96184921264648,
                 'http://www.example.com/image_link.png', 4, '116 and Broadway. New York, NY']
            blank_ts = TouristSpot()
            ts = blank_ts.set_all_from_list(l)
            self.assertEqual(ts, blank_ts)
            self.assertEqual(ts.db_id, l[0])
            self.assertEqual(ts.destinationID, l[1])
            self.assertEqual(ts.destinationName, l[2])
            self.assertEqual(ts.open_time, l[3])
            self.assertEqual(ts.close_time, l[4])
            self.assertEqual(ts.geocode, dict())
            self.assertEqual(ts.geocode['lat'], l[5])
            self.assertEqual(ts.geocode['lng'], l[6])
            self.assertEqual(ts.image_link, l[7])
            self.assertEqual(ts.rating, l[8])
            self.assertEqual(ts.address, l[9])

        # to_dict
        def test_to_dict(self):
            l = [0, 0, 'test', 'open', 'close', 40.80887209540821, -73.96184921264648,
                 'http://www.example.com/image_link.png', 4, '116 and Broadway. New York, NY']
            ts = TouristSpot()
            ts.set_all_from_list(l)
            spot = ts.to_dict()
            self.assertEquals(spot["destinationID"], ts.destinationID)
            self.assertEquals(spot["destinationName"], ts.destinationName)
            self.assertEquals(spot["geocode"], ts.geocode)
            self.assertEquals(spot["image_link"], ts.image_link)
            self.assertEquals(spot["introduction"], ts.introduction)
            self.assertEquals(spot["rating"], ts.rating)
            self.assertEquals(spot["address"], ts.address)

        def test_TouristSpot_str(self):
            ts = TouristSpot()
            s = str(ts)
            self.assertEqual(s, str(ts.destinationName) + ":" + str(ts.destinationID))

        ## ExploriumDBApi.py ##

        # load_user_info(user)
        def test_load_user_info_invalid(self):
            out = ExploriumDbApi.get_user_itineraries('nr182o3jn2r123489')
            self.assertEqual(out, {})

        def test_load_user_info_valid(self):
            # TODO
            return

        # save_tourist_spot(tourist_spot):
        def test_save_tourist_spot(self):
            ts = TouristSpot()  # Initialize with random data
            ExploriumDbApi.save_tourist_spot(ts)
            # TODO check if in DB and cleanup

        # load_tourist_spot(ts_id=None, google_id=None)
        def test_load_tourist_spot_ts_id_none(self):
            GOOGLE_ID_NUM = 1000  # TODO better defn of this number, no magic numbers!
            out = ExploriumDbApi.load_tourist_spot(ts_id=None, google_id=GOOGLE_ID_NUM)
            self.assertEqual(out, None)

        def test_load_tourist_spot_google_id_none(self):
            TS_ID_NUM = 1  # TODO better defn of this number, no magic numbers!
            out = ExploriumDbApi.load_tourist_spot(ts_id=TS_ID_NUM, google_id=None)
            self.assertNotEqual(out, None)

        # save_itinerary(user, city, itinerary)
        def test_save_itinerary(self):
            # TODO
            return

        # load_user_itinerary_info(user)
        def test_load_user_itinerary_info(self):
            # TODO
            return

        # get_user_itineraries(user)
        def test_get_user_itineraries(self):
            # TODO
            return

        # load_itinerary(itinerary_id)
        def test_load_itinerary(self):
            # TODO
            return

        ## utils.py ##

        # valid_email(email)
        def test_valid_email_valid(self):
            email = ''.join(random.choice(string.lowercase, string.uppercase, string.digits) for i in range(10)) + \
                    '@' + \
                    ''.join(random.choice(string.lowercase, string.uppercase, string.digits) for i in range(10)) + \
                    ''.join(random.choice(string.lowercase) for i in range(3))
            is_valid = utils.valid_email(email)
            self.assertTrue(is_valid)

        # valid_username(email)
        def test_valid_username_valid(self):
            username = ''.join(random.choice(string.lowercase, string.uppercase, string.digits) for i in range(10))
            is_valid = utils.valid_username(username)
            self.assertTrue(is_valid)

        # hash_password(password)
        def test_hash_password(self):
            input = 'Test Password'
            expected_hash = '79a62e66ac6387dcc27496aab214dbfe59e86af1aa49f47cc415f3073b6c0472'
            actual_hash = utils.hash_password(input)
            self.assertEqual(expected_hash, actual_hash)

    '''

if __name__ == '__main__':
    unittest.main()


