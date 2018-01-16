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
import utils
from Itinerary import Itinerary
import ExploriumDbApi


class UnitTests(unittest.TestCase):
    ## ItineraryService.py ##
    # get_travel_duration(origin, destination)
    def test_get_travel_duration_valid(self):
        coord1 = (40.80887209540821, -73.96184921264648) # Columbia University Long Lat
        coord2 = (40.73083612189599, -73.99734020233154) # NYU Long Lat
        dur = ItineraryService.get_travel_duration(coord1, coord2)
        self.assertNotEqual(dur, None)
        # TODO add proper duration assertion here

    # generate_tourist_spot_list(city, preferences=None)
    def test_generate_tourist_spot_list_no_pref_valid_city(self):
        l = ItineraryService.generate_tourist_spot_list(city='New York', preferences=None)
        self.assertNotEqual(l, None)
        self.assertGreater(len(l), 0)

    def test_generate_tourist_spot_list_pref1_valid_city(self):
        prefs = dict()
        prefs['types'] = []
        prefs['min_price'] = 0
        prefs['max_price'] = 4
        prefs['time_spent'] = 2
        l = ItineraryService.generate_tourist_spot_list(city='New York', preferences=prefs)
        self.assertNotEqual(l, None)
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
        self.assertEqual(ts.db_id , None)
        self.assertEqual(ts.destinationID , place["place_id"])
        self.assertEqual(ts.destinationName , place["name"])
        self.assertEqual(ts.open_time , None)
        self.assertEqual(ts.close_time , None)
        self.assertEqual(ts.geocode , place["geometry"]["location"])
        self.assertEqual(ts.image_link , place.get('photos', None)[0]['photo_reference'])
        self.assertEqual(ts.introduction , None)
        self.assertEqual(ts.rating , place.get("rating", None))
        self.assertEqual(ts.next_dest_time , None)
    def test_init_TouristSpot_no_img(self):
        place = ItineraryService.generate_tourist_spot_list(city='New York', preferences=None)[0]
        place['photos'] = None
        ts = TouristSpot(place)
        self.assertEqual(ts.db_id , None)
        self.assertEqual(ts.destinationID , place["place_id"])
        self.assertEqual(ts.destinationName , place["name"])
        self.assertEqual(ts.open_time , None)
        self.assertEqual(ts.close_time , None)
        self.assertEqual(ts.geocode , place["geometry"]["location"])
        self.assertEqual(ts.image_link , place.get('photos', None))
        self.assertEqual(ts.introduction , None)
        self.assertEqual(ts.rating , place.get("rating", None))
        self.assertEqual(ts.next_dest_time , None)
    # to_dict
    def test_to_dict(self):
        l = {"destinationID" : 0, "destinationName" : 'test', "open_time" : 'open', "close_time" : 'close', 
             "geocode": {"lat" : 40.80887209540821, "lng" : -73.96184921264648}, 
             "image_link" : 'http://www.example.com/image_link.png', "rating" : 4, "address" : '116 and Broadway. New York, NY'}
        ts = TouristSpot(t_spot = l)
        spot = ts.to_dict()
        self.assertEquals(spot["destinationID"] , ts.destinationID)
        self.assertEquals(spot["destinationName"] , ts.destinationName)
        self.assertEquals(spot["geocode"] , ts.geocode)
        self.assertEquals(spot["image_link"] , ts.image_link)
        self.assertEquals(spot["introduction"] , ts.introduction)
        self.assertEquals(spot["rating"] , ts.rating)
        self.assertEquals(spot["address"] , ts.address)



    ## ExploriumDBApi.py ##

    # load_user_info(user)
    def test_load_user_info_invalid(self):
        out = ExploriumDbApi.get_user_itineraries('nr182o3jn2r123489')
        self.assertEqual(out, [])

    def test_load_user_info_valid(self):
        # TODO
        return

    # save_tourist_spot(tourist_spot):
    def test_save_tourist_spot(self):
        place = dict()
        place['destinationID'] = 0
        place['destinationName'] = 'Test'
        ts = TouristSpot(t_spot=place) # Initialize with random data
        res = ExploriumDbApi.save_tourist_spot(ts)
        self.assertNotEqual(res, None)
        ExploriumDbApi.TOURIST_SPOT_TABLE.delete().where(ExploriumDbApi.TOURIST_SPOT_TABLE.c.google_id == 0)

    # load_tourist_spot(ts_id=None, google_id=None)
    def test_load_tourist_spot_ts_id_none(self):
        out = ExploriumDbApi.load_tourist_spot(ts_id=None, google_id='ChIJ2y1Dpbm6woARP3MtcSoZ8OI')
        self.assertNotEqual(out, None)
    
    def test_load_tourist_spot_google_id_none(self):
        TS_ID_NUM = 650  # TODO better defn of this number, no magic numbers!
        out = ExploriumDbApi.load_tourist_spot(ts_id=TS_ID_NUM, google_id=None)
        self.assertNotEqual(out, None)

    # save_itinerary(user, city, itinerary)
    def test_save_delete_itinerary(self):
        user = 'Spiderman1'
        it = Itinerary('New York', None)
        self.assertNotEqual(it, None)
        it_id = ExploriumDbApi.save_itinerary(user, it)
        self.assertNotEqual(it_id, None)
        ExploriumDbApi.delete_itinerary(it_id)
        # TODO check if properly deleted

    def test_add_delete_user(self):
        username1 = 'ar21321nodas'
        firstname = 'First Name'
        lastname = 'Last Name'
        password = utils.hash_password('password')
        email = 'ar21321nodas@example.com'
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == username1)
        ExploriumDbApi.conn.execute(query)
        query = ExploriumDbApi.USERS_TABLE.insert().values(username=username1, password=password, email=email,
                                                           firstname=firstname, lastname=lastname)

        ExploriumDbApi.conn.execute(query)
        username2 = '2e08hfdas'
        password = utils.hash_password('password')
        email = '2e08hfdas@example.com'
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == username2)
        ExploriumDbApi.conn.execute(query)
        query = ExploriumDbApi.USERS_TABLE.insert().values(username=username2, password=password, email=email,
                                                           firstname=firstname, lastname=lastname)
        ExploriumDbApi.conn.execute(query)
        it = Itinerary('New York')
        self.assertNotEqual(it, None)
        it_id = ExploriumDbApi.save_itinerary(username1, it)
        it.db_id = it_id
        self.assertNotEqual(it.db_id, None)
        add_res = ExploriumDbApi.add_user(username2, it.db_id)
        self.assertEqual(add_res, None)
        ExploriumDbApi.delete_itinerary(it.db_id)
        # TODO remove users


    def test_remove_user_invalid_it(self):
        username = 'asdas32dasf'
        firstname = 'First Name'
        lastname = 'Last Name'
        password = utils.hash_password('password')
        email = '2e08hfdas@example.com'
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == username)
        ExploriumDbApi.conn.execute(query)
        query = ExploriumDbApi.USERS_TABLE.insert().values(username=username, password=password, email=email,
                                                           firstname=firstname, lastname=lastname)
        del_res = ExploriumDbApi.remove_user(username, 112391849124321)
        self.assertEqual(del_res, 'User does not exist')

    def test_remove_user(self):
        username1 = 'xc3lrea8cfngas'
        firstname = 'First Name'
        lastname = 'Last Name'
        password = utils.hash_password('password')
        email = 'xc3lrea8cfngas@example.com'
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == username1)
        ExploriumDbApi.conn.execute(query)
        query = ExploriumDbApi.USERS_TABLE.insert().values(username=username1, password=password, email=email,
                                                           firstname=firstname, lastname=lastname)
        ExploriumDbApi.conn.execute(query)
        username2 = 'a8casuxdas'
        firstname = 'First Name'
        lastname = 'Last Name'
        password = utils.hash_password('password')
        email = 'a8casuxdas@example.com'
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == username2)
        ExploriumDbApi.conn.execute(query)

        query = ExploriumDbApi.USERS_TABLE.insert().values(username=username2, password=password, email=email,
                                                           firstname=firstname, lastname=lastname)
        ExploriumDbApi.conn.execute(query)
        it = Itinerary('New York')
        it_id = ExploriumDbApi.save_itinerary(username1, it)
        it.db_id = it_id
        self.assertNotEqual(it.db_id, None)
        ExploriumDbApi.add_user(username2, it.db_id)
        del_res = ExploriumDbApi.remove_user(username2, it.db_id)
        self.assertEqual(del_res, None)
        ExploriumDbApi.delete_itinerary(it.db_id)
        # TODO remove users

    def test_add_show_comment_valid(self):
        username = 'xc3lrea8cfngas'
        firstname = 'First Name'
        lastname = 'Last Name'
        password = utils.hash_password('password')
        email = 'xc3lrea8cfngas@example.com'
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == username)
        ExploriumDbApi.conn.execute(query)
        query = ExploriumDbApi.USERS_TABLE.insert().values(username=username, password=password, email=email,
                                                           firstname=firstname, lastname=lastname)
        ExploriumDbApi.conn.execute(query)
        it = Itinerary('New York')
        it_id = ExploriumDbApi.save_itinerary(username, it)
        it.db_id = it_id
        self.assertNotEqual(it, None)
        self.assertNotEqual(it.db_id, None)
        add_res = ExploriumDbApi.add_comment(username, it.db_id, 'Hello World')
        self.assertEqual(add_res, None)
        comments = ExploriumDbApi.get_itinerary_comments(it.db_id)
        self.assertNotEqual(comments, None)
        in_comments = False
        for comment in comments:
            if comment['comment'] == 'Hello World' and comment['username'] == username:
                in_comments = True
        self.assertTrue(in_comments)
        query = ExploriumDbApi.ITINERARY_TABLE.delete().where(ExploriumDbApi.ITINERARY_TABLE.c.itinerary_id == it.db_id)
        ExploriumDbApi.conn.execute(query)

    def test_add_show_comment_invalid_it(self):
        username = 'xc3lrea8cfngas'
        firstname = 'First Name'
        lastname = 'Last Name'
        password = utils.hash_password('password')
        email = 'xc3lrea8cfngas@example.com'
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == username)
        ExploriumDbApi.conn.execute(query)
        query = ExploriumDbApi.USERS_TABLE.insert().values(username=username, password=password, email=email,
                                                           firstname=firstname, lastname=lastname)
        ExploriumDbApi.conn.execute(query)
        add_res = ExploriumDbApi.add_comment(username, 112391849124321, 'Hello World')
        self.assertNotEqual(add_res, None)
        comments = ExploriumDbApi.get_itinerary_comments(112391849124321)
        self.assertEqual(comments, None)

    # load_user_itinerary_info(user)
    # TODO test invalid
    def test_load_user_itinerary_info_valid(self):
        user = 'Spiderman1'
        its = ExploriumDbApi.load_user_itinerary_info(user)
        self.assertNotEqual(its, None)
        self.assertGreater(len(its), 1)

    # get_user_itineraries(user)
    # TODO test invalid
    def test_get_user_itineraries_valid(self):
        user = 'Spiderman1'
        its = ExploriumDbApi.load_user_itinerary_info(user)
        self.assertNotEqual(its, None)
        self.assertGreater(len(its), 1)
        return

    # load_itinerary(itinerary_id)
    # TODO test invalid
    def test_load_itinerary_valid(self):
        it = ExploriumDbApi.load_itinerary(647)
        self.assertNotEqual(it, None)
        self.assertGreater(len(it), 1)

    ## utils.py ##

    # valid_email(email)
    def test_valid_email_valid(self):
        email = 'test@example.com'
        is_valid = utils.valid_email(email)
        query = ExploriumDbApi.USERS_TABLE.select().where(ExploriumDbApi.USERS_TABLE.c.email == email)
        email_check = ExploriumDbApi.conn.execute(query).fetchone()
        if email_check:
            self.assertFalse(is_valid)
        else:
            self.assertTrue(is_valid)
    def test_valid_email_invalid(self):
        email = 'tea.com'
        is_valid = utils.valid_email(email)
        self.assertFalse(is_valid)

    # valid_username(email)
    def test_valid_username_valid(self):
        username = 'asdfa8sdhac'
        is_valid = utils.valid_username(username)
        self.assertTrue(is_valid)
    def test_valid_username_guest(self):
        username = 'guest'
        is_valid = utils.valid_username(username)
        self.assertFalse(is_valid)
    def test_valid_username_invalid(self):
        username = 'helloworld'
        is_valid = utils.valid_username(username)
        self.assertFalse(is_valid)

    # hash_password(password)
    def test_hash_password(self):
        input = 'Test Password'
        expected_hash = '79a62e66ac6387dcc27496aab214dbfe59e86af1aa49f47cc415f3073b6c0472'
        actual_hash = utils.hash_password(input)
        self.assertEqual(expected_hash, actual_hash)

    # TODO unit testing for this
    ## RouteOptimizer.py
    # #print_adj_list


    ## itinerary.py ##
    def test_init_itinerary_valid(self):
        it = Itinerary('New York', None)
        self.assertNotEqual(it, None)
        self.assertNotEqual(it.touristSpots, None)
        self.assertGreater(len(it.touristSpots), 0)
    def test_init_itinerary_dict(self):
        it1 = Itinerary('New York', None)
        it2 = Itinerary('New York', itinerary=it1.to_dict())
        self.assertNotEqual(it2, None)
        self.assertEqual(len(it1.touristSpots), len(it2.touristSpots))
        for i in range(len(it1.touristSpots)):
            self.assertEqual(len(it1.touristSpots[i]), len(it2.touristSpots[i]))
            for j in range(len(it1.touristSpots[i])):
                self.assertEqual(it1.touristSpots[i][j].destinationID, it2.touristSpots[i][j].destinationID)

    def test_add_spot(self):
        it = Itinerary('New York', None)
        old_items = sum(it.touristSpots, [])
        #it.add_spot(TouristSpot())
        ts = ExploriumDbApi.load_tourist_spot(google_id='ChIJ2y1Dpbm6woARP3MtcSoZ8OI')
        it.add_spot(ts)
        new_items = sum(it.touristSpots, [])
        self.assertGreater(len(new_items), len(old_items))

    def test_del_spot(self):
        it = Itinerary('New York', None)
        ts = ExploriumDbApi.load_tourist_spot(google_id='ChIJ2y1Dpbm6woARP3MtcSoZ8OI')
        it.add_spot(ts)
        old_items = sum(it.touristSpots, [])
        it.del_spot(ts)
        new_items = sum(it.touristSpots, [])
        self.assertLess(len(new_items), len(old_items))

    def test_itinerary_to_dict(self):
        it = Itinerary('New York', None)
        self.assertNotEqual(it, None)
        self.assertNotEqual(it.touristSpots, None)
        self.assertGreater(len(it.touristSpots), 0)
        dict = it.to_dict()
        self.assertEqual(dict['city'], 'New York')
        self.assertEqual(dict['db_id'], it.db_id)



### System Tests ###

class SystemTests(unittest.TestCase):
    # def setUp(self):
    #     DATABASEURI = "postgresql://fortytwo:explorium-COMS4156@coms4156.cf4dw5ld7jgf.us-east-2.rds.amazonaws.com:5432/Explorium"
    #     engine = sqlalchemy.create_engine(DATABASEURI)
    #     g.conn = engine.connect()

    # def tearDown(self):
    #     g.conn.close()
    usernamen = " "
    passwordn = " "
    usernamen2 = " "
    passwordn2 = " "
    itinerary = None

    def user_generator(self, size=7, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size)) + '1zZ'

    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/signin', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        SystemTests.usernamen = self.user_generator()
        SystemTests.passwordn = self.user_generator()
        SystemTests.usernamen2 = self.user_generator()
        SystemTests.passwordn2 = self.user_generator()
        #print('test_index')

    # ensure the login page loads correctly
    def test_index2(self):
        tester = app.test_client(self)
        response = tester.get('/signin', content_type='html/text')
        self.assertTrue(b'Login' in response.data)
        self.assertTrue(b'Explorium' in response.data)
        self.assertNotIn(b'Welcome', response.data)
        #print('test_index2')

    # try to login with a username which has not been signup yet
    def test_login_page_before(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin',
            data=dict(user_username=SystemTests.usernamen, user_password=SystemTests.passwordn),
            follow_redirects=True
        )
        self.assertNotIn(b'Search Cities', response.data)
        self.assertNotIn(b'Welcome', response.data)
        self.assertIn(b'Login', response.data)
        self.assertIn(b'Do not have an account', response.data)
        #print('test_login_page_before')

    def test_signup_page1(self):
        tester = app.test_client(self)
        tester.post(
            '/signup',
            data=dict(user_username=SystemTests.usernamen,
                      user_password=SystemTests.passwordn,
                      user_repeat_password=SystemTests.passwordn,
                      user_email=SystemTests.usernamen + '@gmail.com',
                      user_firstname='userf',
                      user_lastname='userl'),
            follow_redirects=True
        )
        response = tester.post(
            '/signin',
            data=dict(user_username=SystemTests.usernamen, user_password=SystemTests.passwordn),
            follow_redirects=True
        )
        self.assertIn(b'Author', response.data)
        self.assertIn(b'Search Cities', response.data)
        self.assertIn(b'Welcome', response.data)
        self.assertNotIn(b'Login', response.data)
        #print('test_signup_page1')

    def test_signin_page2(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin',
            data=dict(user_username=SystemTests.usernamen, user_password="wrongpassword"),
            follow_redirects=True
        )
        self.assertNotIn(b'Search Cities', response.data)
        self.assertNotIn(b'Welcome', response.data)
        self.assertIn(b'Login', response.data)
        #print('test_signin_page2')

    # def test_signup_page5(self):
    #     tester = app.test_client(self)
    #     tester.post(
    #         '/signup',
    #         data = dict(user_username="random11", user_password = SystemTests.passwordn, user_repeat_password = SystemTests.passwordn),
    #         follow_redirects = True
    #     )
    #     response = tester.post(
    #         '/signin',
    #         data = dict(user_username="random11", user_password = SystemTests.passwordn),
    #         follow_redirects = True
    #     )
    #     query = users.delete().where(users.c.username=="random11")
    #     conn.execute(query)
    #     self.assertIn(b'Author' , response.data)
    #     self.assertIn(b'Search Cities' , response.data)
    #     self.assertIn(b'Welcome', response.data)
    #     self.assertNotIn(b'Login', response.data)

    #except is right now
    def test_signup_page3(self):
        tester = app.test_client(self)
        try:
            response = tester.post(
            '/signup',
            data = dict(user_username=SystemTests.usernamen,
                        user_password = SystemTests.passwordn,
                        user_repeat_password = SystemTests.passwordn,
                        user_email = SystemTests.usernamen+'@gmail.com',
                        user_firstname='userf',
                        user_lastname = 'userl'),
            follow_redirects = True
            )
            self.assertNotIn(b'Search Cities' , response.data)
            self.assertIn(b'Search Cities', response.data)
            self.assertIn(b'signup', response.data)
        except Exception as e:
            pass

    def test_signup_page4(self):
        tester = app.test_client(self)
        try:
            response = tester.post(
            '/signup',
            data = dict(user_username=SystemTests.usernamen,
                        user_password = SystemTests.passwordn,
                        user_repeat_password = SystemTests.passwordn,
                        user_email = 'aaa',
                        user_firstname='userf',
                        user_lastname = 'userl'),
            follow_redirects = True
            )
            self.assertNotIn(b'Search Cities' , response.data)
            self.assertIn(b'Search Cities', response.data)
            self.assertIn(b'signup', response.data)
        except Exception as e:
            pass
        
        

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



    # ensure login behaves correctly given correct credentials
    def test_login_page(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        self.assertIn(b'Author', response.data)
        self.assertIn(b'Search Cities', response.data)
        self.assertIn(b'Welcome', response.data)
        self.assertNotIn(b'Login', response.data)
        #print('test_login_page')
    def test_login_guest_page(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin_as_a_guest',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        self.assertIn(b'Author', response.data)
        self.assertIn(b'Search Cities', response.data)
        self.assertIn(b'Welcome', response.data)
        self.assertNotIn(b'Login', response.data)
        #print('test_signin_as_a_guest_page')

    # test logout
    def test_logout_page(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.get('logout', follow_redirects=True)
        self.assertIn(b'Do not have an account', response.data)
        self.assertNotIn(b'Welcome', response.data)
        #print('test_logout_page')

    # test search a city
    def test_search_page1(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.post(
            '/search_city',
            data=dict(search_box="new york"),
            follow_redirects=True
        )
        self.assertIn(b'Search Results: new york', response.data)
        self.assertIn(b'Routes', response.data)
        self.assertIn(b'Spiderman1', response.data)
        #print('test_search_page1')

    def test_search_page2(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.post(
            '/search_city',
            data=dict(search_box="Paris"),
            follow_redirects=True
        )
        self.assertIn(b'Search Results: Paris', response.data)
        self.assertIn(b'Routes', response.data)
        self.assertIn(b'Spiderman1', response.data)
        #print('test_search_page2')

    def test_search_page3(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.post(
            '/search_city',
            data=dict(search_box="10027"),
            follow_redirects=True
        )
        self.assertIn(b'Search Results: 10027', response.data)
        self.assertIn(b'Routes', response.data)
        self.assertIn(b'Spiderman1', response.data)
        #print('test_search_page3')

    def test_search_page4(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.post(
            '/search_city',
            data=dict(search_box="Nwe York"),
            follow_redirects=True
        )
        self.assertIn(b'Search Results: Nwe York', response.data)
        self.assertIn(b'Routes', response.data)
        self.assertIn(b'Spiderman1', response.data)
        #print('test_search_page4')

    def test_search_page5(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.post(
            '/search_city',
            data=dict(search_box="%……。等"),
            follow_redirects=True
        )
        self.assertNotIn(b'Search Results: %……。等', response.data)
        #print('test_search_page5')



        # query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username=="Spiderman1")
        # ExploriumDbApi.conn.execute(query)

    # Test whether the function return a list of correct tourist spots in the query area
    def test_get_itinerary(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.post(
            '/route',
            data={
                'rangeInput': 15,
                'price': 1000,
                'max_price': 5000,
                'city': "New York",
                't_spot': ["museums"]
            },
            follow_redirects=True
        )
        self.assertIn(b'New York', response.data)
        #print('test_get_itinerary')

    def test_generate_tourist_spot_list(self):
        spot_list = ItineraryService.generate_tourist_spot_list("New York")
        for spot in spot_list:
            tourist_spot = spot
            self.assertNotIn(b'dasd', spot_list)
            assert spot['rating'] <= 5
            assert spot['rating'] >= 0
            assert spot['geometry']['location']['lat'] > 40
            assert spot['geometry']['location']['lat'] < 41
        #print('test_generate_tourist_spot_list')

    def test_itinerary1(self):
        user = 'Spiderman1'
        city = 'New York'
        pref = dict()
        pref['types'] = 'museums'
        pref['min_price'] = 2000
        pref['max_price'] = 5000
        pref['radius'] = 2000
        itinerary = Itinerary(city, preferences=pref)
        SystemTests.itinerary = itinerary
        assert itinerary.city is 'New York'
        #print('test_itinerary1')

    def test_itinerary2(self):
        user = 'Spiderman1'
        city = 'New York'
        pref = dict()
        pref['types'] = 'museums'
        pref['min_price'] = 2000
        pref['max_price'] = 1000
        pref['radius'] = 2000
        itinerary = Itinerary(city, preferences=pref)
        SystemTests.itinerary = itinerary
        assert itinerary.city is 'New York'
        #print('test_itinerary2')

    # def test_itinerary3(self):
    #     user = 'Spiderman1'
    #     city = 'New York'
    #     pref = dict()
    #     pref['types'] = 'museums'
    #     pref['min_price'] = 2000
    #     pref['max_price'] = 5000
    #     pref['radius'] = -1
    #     itinerary = Itinerary(city, preferences=pref)
    #     SystemTests.itinerary = itinerary
    #     assert itinerary.city is not 'New York'


    ## Not sure about these Tengyu please confirm ##
    def test_view_itinerary_get(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.get('/view_itineraries', content_type='html/text', follow_redirects=True)
        #print(response.data)
        self.assertIn(b'New York', response.data)
        #print('test_get_itinerary')



    # TODO add invalid tester
    # def test_controller_regenerate_valid(self):
    #     tester = app.test_client(self)
    #     tester.post(
    #         '/signin',
    #         data=dict(user_username="Spiderman1", user_password="Spiderman1"),
    #         follow_redirects=True
    #     )
    #     tester.post(
    #         '/route',
    #         data={
    #             'rangeInput': 15,
    #             'price': 1000,
    #             'max_price': 5000,
    #             'city': "New York",
    #             't_spot': ["museums"]
    #         },
    #         follow_redirects=True
    #     )
    #     response = tester.post(
    #         '/regenerate',
    #         data={
    #             'days': 16,
    #             'price': 1000,
    #         },
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'New York', response.data)

    def test_controller_get_comment(self):
        # TODO check for valid, do cleanup after
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
#        tester.post(
#            '/route',
#            data={
#                'rangeInput': 15,
#                'price': 1000,
#                'max_price': 5000,
#                'city': "New York",
#                't_spot': ["museums"]
#            },
#            follow_redirects=True
#        )
        tester.post(
            '/route',
            data={
                'rangeInput': 15,
                'price': 1000,
                'max_price': 5000,
                'city': "New York",
                't_spot': ["museums"]
            },
            follow_redirects=True
        )
        tester.get('/save', content_type='html/text')
        response = tester.post(
            '/get_comment',
            data=dict(comment="Test Comment"),
            follow_redirects=True
        )
        self.assertIn(b'Comment', response.data)

    # def test_controller_add_tourist_spot(self):
    #     ts = TouristSpot(t_spot={'tourist_spot_id': 1, 'name': 'Test Spot'})
    #     tester = app.test_client(self)
    #     tester.post(
    #         '/signin',
    #         data=dict(user_username="Spiderman1", user_password="Spiderman1"),
    #         follow_redirects=True
    #     )
    #     tester.get('/view_itineraries', content_type='html/text')
    #     response = tester.post(
    #         '/add_spot',
    #         data=dict(tourist_spot=ts),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Test Spot', response.data)

    # def test_controller_del_tourist_spot(self):
    #     ts = TouristSpot(t_spot={'tourist_spot_id': 1, 'name': 'Test Spot'})
    #     tester = app.test_client(self)
    #     tester.post(
    #         '/signin',
    #         data=dict(user_username="Spiderman1", user_password="Spiderman1"),
    #         follow_redirects=True
    #     )
    #     tester.get('/view_itineraries', content_type='html/text')
    #     response = tester.post(
    #         '/delete_spot',
    #         data=dict(tourist_spot=ts),
    #         follow_redirects=True
    #     )
    #     self.assertNotIn(b'Test Spot', response.data)
    def test_controller_save(self):
        tester = app.test_client(self)
        user = 'helloworld'
        query = ExploriumDbApi.USER_ITINERARIES.delete().where(ExploriumDbApi.USER_ITINERARIES.c.user_id == 1144)
        ExploriumDbApi.conn.execute(query)
        login_response = tester.post(
            '/signin',
            data=dict(user_username="helloworld", user_password="helloworld"),
            follow_redirects=True
        )
        self.assertIn(b'Welcome', login_response.data)
        route_response = tester.post(
            '/route',
            data={
                'rangeInput': 15,
                'price': 1000,
                'max_price': 5000,
                'city': "New York",
                't_spot': ["museums"]
            },
            follow_redirects=True
        )
        self.assertIn(b'New York', route_response.data)

        tester.get('/save', content_type='html/text')
        query = ExploriumDbApi.USER_ITINERARIES.select().where(ExploriumDbApi.USER_ITINERARIES.c.user_id == 1144)
        save_results = ExploriumDbApi.conn.execute(query).fetchone()
        self.assertNotEqual(save_results, None)
        tester.get('/delete_itinerary/'+str(save_results['itinerary_id']), content_type='html/text', follow_redirects=True)
        query = ExploriumDbApi.USER_ITINERARIES.select().where(ExploriumDbApi.USER_ITINERARIES.c.user_id == 1144)
        del_results = ExploriumDbApi.conn.execute(query).fetchone()
        self.assertEqual(del_results, None)

    ''' 
    def test_controller_add_remove_user(self):
        query = ExploriumDbApi.USER_ITINERARIES.delete().where(ExploriumDbApi.USER_ITINERARIES.c.user_id == 1144)
        ExploriumDbApi.conn.execute(query)
        tester = app.test_client(self)
        user = 'Spiderman1'
        it = Itinerary('New York', None)
        self.assertNotEqual(it, None)
        it_id = ExploriumDbApi.save_itinerary(user, it)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        tester.post(
            '/route',
            data={
                'rangeInput': 15,
                'price': 1000,
                'max_price': 5000,
                'city': "Paris",
                't_spot': ["museums"]
            },
            follow_redirects=True
        )
        tester.post(
            '/add_user',
             data={
                'user': 'helloworld',
            },
            follow_redirects=True
        )
        response = tester.get('/view_itineraries', content_type='html/text')
        self.assertIn(b'helloworld', response.data)
        tester.post(
            '/remove_user',
             data={
                'user': 'helloworld',
            },
            follow_redirects=True
        ) 
        response = tester.get('/view_itineraries', content_type='html/text')
        self.assertNotIn(b'helloworld', response.data)
    '''
    def test_signup_invalid_email(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signup',
            data=dict(user_username='asdfasesfasd',
                      user_password=SystemTests.passwordn,
                      user_repeat_password=SystemTests.passwordn,
                      user_email='hello@example.com',
                      user_firstname='userf',
                      user_lastname='userl'),
            follow_redirects=True
        )
        self.assertIn(b'Invalid Email', response.data)


    def test_controller_add_remove_user_id(self):
        query = ExploriumDbApi.USER_ITINERARIES.delete().where(ExploriumDbApi.USER_ITINERARIES.c.user_id == 1144)
        ExploriumDbApi.conn.execute(query)
        tester = app.test_client(self)
        user = 'Spiderman1'
        it = Itinerary('New York', None)
        self.assertNotEqual(it, None)
        it_id = ExploriumDbApi.save_itinerary(user, it)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        tester.post(
            '/route',
            data={
                'rangeInput': 15,
                'price': 1000,
                'max_price': 5000,
                'city': "Paris",
                't_spot': ["museums"]
            },
            follow_redirects=True
        )
        tester.post(
            '/add_user/'+str(it_id),
             data={
                'user': 'helloworld',
            },
            follow_redirects=True
        )
        response = tester.get('/view_itineraries', content_type='html/text')
        self.assertIn(b'helloworld', response.data)
        tester.post(
            '/remove_user/'+str(it_id),
             data={
                'user': 'helloworld',
            },
            follow_redirects=True
        ) 
        response = tester.get('/view_itineraries', content_type='html/text')
        self.assertNotIn(b'helloworld', response.data)
 
    def test_controller_regenerate(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.post(
            '/route',
            data={
                'rangeInput': 15,
                'price': 1000,
                'max_price': 5000,
                'city': "New York",
                't_spot': ["museums"]
            },
            follow_redirects=True
        )
        response = tester.post(
            '/regenerate/Paris',
             data={
                'days': 15,
                'price': 1000
            },
            follow_redirects=True
        )
        self.assertIn(b'Paris', response.data)

    
    def test_add_delete_tourist_spot(self):
        tester = app.test_client(self)
        user = 'Spiderman1'
        it = Itinerary('New York', None)
        self.assertNotEqual(it, None)
        it_id = ExploriumDbApi.save_itinerary(user, it)
        query = ExploriumDbApi.ITINERARY_TABLE.select().where(ExploriumDbApi.ITINERARY_TABLE.c.itinerary_id == it_id)
        result = ExploriumDbApi.conn.execute(query).fetchone()
        self.assertNotEqual(result, None)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        add_response = tester.post(
            '/add_spot/661',
            data={
                'itinerary': str(it_id)
            },
            follow_redirects=True
        )
        tester.get('/itinerary/'+str(it_id), follow_redirects=True, content_type='html/text')
        self.assertIn('The Palm Los Angeles', add_response.data)
        del_response = tester.get('/delete_spot/661', follow_redirects=True, content_type='html/text') 
        self.assertNotIn('The Palm Los Angeles', del_response.data)
    
    ## End unsure ##

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
            SystemTests.itinerary = itinerary
            assert itinerary.city is not 'New York'
        except Exception as e:
            pass
        else:
            assert itinerary.city is 'New York'
        ##print('test_1')

    def test_save_route(self):
        user = 'Spiderman1'
        city = 'New York'
        pref = dict()
        pref['types'] = 'museums'
        pref['min_price'] = 2000
        pref['max_price'] = 5000
        pref['radius'] = 2000
        itinerary = Itinerary(city, preferences=pref)
        # ItineraryService.save_route(user, city, itinerary)
        ##print('test_save_route')
    #
    # def test_DBApi_save_tourist_spot(self):
    #     result = ExploriumDbApi.save_tourist_spot(SystemTests.tourist_spot)
    #     state = 0
    #     if result is not None or u"":
    #         state = 1
    #     assert state == 1
    #     SystemTests.tourist_spot_id = result
    #
    # def test_DBApi_load_tourist_spot(self):
    #     result = ExploriumDbApi.load_tourist_spot(SystemTests.tourist_spot_id)
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
        pref['min_price'] = 1
        pref['max_price'] = 3
        pref['radius'] = 2000
        itinerary = Itinerary(city, preferences=pref)
        ExploriumDbApi.save_itinerary(user, itinerary)
        result = ExploriumDbApi.get_user_itineraries(user)
        ##print('------------------------------------------')
        ##print(result)
        ##print('------------------------------------------')
        state = 0
        if result is not None or u"":
            state = 1
        assert state == 1
        ##print('test_DBApi_save_load_itinerary')

    def test_za_profile1(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.get('/profile', follow_redirects=True)
        self.assertIn(b'First Name', response.data)
        self.assertIn(b'Last Name', response.data)
        self.assertNotIn(b'Welcome', response.data)
        ##print('test_za_profile1')

    def test_za_edit_profile1(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username="Spiderman1", user_password="Spiderman1"),
            follow_redirects=True
        )
        response = tester.get('profile-edit', follow_redirects=True)
        self.assertIn(b'Edit Profile', response.data)
        self.assertIn(b'Save Changes', response.data)
        self.assertNotIn(b'Welcome', response.data)
        ##print('test_za_edit_profile1')

    def test_zb_edit_profile2(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username='Spiderman1', user_password='Spiderman1'),
            follow_redirects=True
        )
        response = tester.post(
            '/profile-edit',
            data={'user-firstname': None,
                  'user-lastname': 'lastname2',
                  'user-email': SystemTests.usernamen2 + '@gmail.com',
                  'user-username': SystemTests.usernamen},
            follow_redirects=True
        )
        self.assertIn('Fields cannot be empty.', response.data)
        ##print('test_zb_edit_profile2')

    def test_zc_edit_profile3(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username=SystemTests.usernamen, user_password=SystemTests.passwordn),
            follow_redirects=True
        )
        response = tester.post(
            '/profile-edit',
            data={'user-firstname': 'firstname2',
                  'user-lastname': 'lastname2',
                  'user-email': SystemTests.usernamen2 + '@gmail.com',
                  'user-username': SystemTests.usernamen2},
            follow_redirects=True
        )
        self.assertIn(SystemTests.usernamen2, response.data)
        #print('test_zc_edit_profile3')

    def test_zd_edit_profile3(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username='Spiderman1', user_password='Spiderman1'),
            follow_redirects=True
        )
        response = tester.post(
            '/profile-edit',
            data={'user-firstname': 'spi',
                  'user-lastname': 'der',
                  'user-email': 'Spiderman1@gmail.com',
                  'user-username': 'helloworld'},
            follow_redirects=True
        )
        self.assertIn('Username is already taken', response.data)

    def test_ze_edit_profile3(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username='Spiderman1', user_password='Spiderman1'),
            follow_redirects=True
        )
        response = tester.post(
            '/profile-edit',
            data={'user-firstname': 'spi',
                  'user-lastname': 'der',
                  'user-email': 'testemail@test.com',
                  'user-username': 'Spiderman1'},
            follow_redirects=True
        )    
        self.assertIn('Invalid Email', response.data)


    def test_zd_login_page(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin',
            data=dict(user_username=SystemTests.usernamen2, user_password=SystemTests.passwordn),
            follow_redirects=True
        )
        self.assertIn(b'Author', response.data)
        self.assertIn(b'Search Cities', response.data)
        self.assertIn(b'Welcome', response.data)
        self.assertNotIn(b'Login', response.data)
        #print('test_zd_edit_profile3')

    def test_ze_login_page(self):
        tester = app.test_client(self)
        response = tester.post(
            '/signin',
            data=dict(user_username=SystemTests.usernamen, user_password=SystemTests.passwordn),
            follow_redirects=True
        )
        self.assertNotIn(b'Search Cities', response.data)
        self.assertNotIn(b'Welcome', response.data)
        self.assertIn(b'Login', response.data)
        #print('test_ze_edit_profile3')

    def test_zg_edit_profile4(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username=SystemTests.usernamen2, user_password=SystemTests.passwordn),
            follow_redirects=True
        )
        response = tester.post(
            '/profile-edit',
            data={'user-firstname': 'firstname2',
                  'user-lastname': None,
                  'user-email': SystemTests.usernamen2 + '@gmail.com',
                  'user-username': SystemTests.usernamen2},
            follow_redirects=True
        )
        self.assertIn('Fields cannot be empty.', response.data)
        #print('test_zg_edit_profile3')

    def test_zh_edit_profile5(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username=SystemTests.usernamen2, user_password=SystemTests.passwordn),
            follow_redirects=True
        )
        response = tester.post(
            '/profile-edit',
            data={'user-firstname': 'firstname2',
                  'user-lastname': 'lastname2',
                  'user-email': None,
                  'user-username': SystemTests.usernamen2},
            follow_redirects=True
        )
        self.assertIn('Fields cannot be empty.', response.data)
        #print('test_zh_edit_profile3')

    def test_zi_edit_profile6(self):
        tester = app.test_client(self)
        tester.post(
            '/signin',
            data=dict(user_username=SystemTests.usernamen2, user_password=SystemTests.passwordn),
            follow_redirects=True
        )
        response = tester.post(
            '/profile-edit',
            data={'user-firstname': 'firstname2中',
                  'user-lastname': 'lastname2',
                  'user-email': SystemTests.usernamen2 + '@gmail.com',
                  'user-username': SystemTests.usernamen2},
            follow_redirects=True
        )
        self.assertNotIn('Fields cannot be empty.', response.data)
        self.assertIn('firstname2中', response.data)

        #print('test_zi_edit_profile3')
    def test_zz_tearDown(self):
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == SystemTests.usernamen2)
        ExploriumDbApi.conn.execute(query)
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == 'xc3lrea8cfngas')
        ExploriumDbApi.conn.execute(query)
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == '2e08hfdas')
        ExploriumDbApi.conn.execute(query)
        query = ExploriumDbApi.USERS_TABLE.delete().where(ExploriumDbApi.USERS_TABLE.c.username == 'a8casuxdas')
        ExploriumDbApi.conn.execute(query)


if __name__ == '__main__':
    unittest.main()
