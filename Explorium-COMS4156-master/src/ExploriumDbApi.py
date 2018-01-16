import json, sqlalchemy
from sqlalchemy import and_, asc
from TouristSpot import TouristSpot
import datetime
import Itinerary

DATABASEURI = "postgresql://fortytwo:explorium-COMS4156@coms4156.cf4dw5ld7jgf.us-east-2.rds.amazonaws.com:5432/Explorium"
engine = sqlalchemy.create_engine(DATABASEURI)
engine.echo = False
conn = engine.connect()

TOURIST_SPOT_TABLE = sqlalchemy.Table('tourist_spot', sqlalchemy.MetaData(),
                                      sqlalchemy.Column('tourist_spot_id', sqlalchemy.INTEGER, primary_key=True),
                                      sqlalchemy.Column('google_id', sqlalchemy.VARCHAR(100)),
                                      sqlalchemy.Column('name', sqlalchemy.VARCHAR(100), nullable=False),
                                      sqlalchemy.Column('open_time', sqlalchemy.TIME),
                                      sqlalchemy.Column('close_time', sqlalchemy.TIME),
                                      sqlalchemy.Column('latitude', sqlalchemy.NUMERIC),
                                      sqlalchemy.Column('longitude', sqlalchemy.NUMERIC),
                                      sqlalchemy.Column('image_link', sqlalchemy.VARCHAR(255)),
                                      sqlalchemy.Column('rating', sqlalchemy.REAL),
                                      sqlalchemy.Column('address', sqlalchemy.VARCHAR(255)),
                                      sqlalchemy.Column('last_updated', sqlalchemy.TIMESTAMP)
                                      )
USERS_TABLE = sqlalchemy.Table('users', sqlalchemy.MetaData(),
                               sqlalchemy.Column('user_id', sqlalchemy.INTEGER, primary_key=True),
                               sqlalchemy.Column('password', sqlalchemy.VARCHAR(20), nullable=False),
                               sqlalchemy.Column('username', sqlalchemy.VARCHAR(20), nullable=False),
                               sqlalchemy.Column('firstname', sqlalchemy.VARCHAR(20)),
                               sqlalchemy.Column('lastname', sqlalchemy.VARCHAR(20)),
                               sqlalchemy.Column('email', sqlalchemy.VARCHAR(50))
                              )
ITINERARY_TABLE = sqlalchemy.Table('itinerary', sqlalchemy.MetaData(),
                                   sqlalchemy.Column('itinerary_id', sqlalchemy.INTEGER, primary_key=True),
                                   sqlalchemy.Column('city', sqlalchemy.VARCHAR(20), nullable=False)
                                   )
USER_ITINERARIES = sqlalchemy.Table('user_itineraries', sqlalchemy.MetaData(),
                                    sqlalchemy.Column('itinerary_id', sqlalchemy.INTEGER, nullable=False),
                                    sqlalchemy.Column('user_id', sqlalchemy.INTEGER, nullable=False),
                                    sqlalchemy.Column('privilege', sqlalchemy.VARCHAR(20))
                                    )
ITINERARY_SPOTS = sqlalchemy.Table('itinerary_spots', sqlalchemy.MetaData(),
                                   sqlalchemy.Column('itinerary_id', sqlalchemy.INTEGER, nullable=False),
                                   sqlalchemy.Column('tourist_spot_id', sqlalchemy.INTEGER, nullable=False),
                                   sqlalchemy.Column('destination_num', sqlalchemy.INTEGER, nullable=False),
                                   sqlalchemy.Column('time_to_next_dest', sqlalchemy.VARCHAR(20)),
                                   sqlalchemy.Column('day_num', sqlalchemy.INTEGER)
                                  )

COMMENTS = sqlalchemy.Table('comments', sqlalchemy.MetaData(),
                            sqlalchemy.Column('itinerary_id', sqlalchemy.INTEGER, nullable=False),
                            sqlalchemy.Column('user_id', sqlalchemy.INTEGER, primary_key=True),
                            sqlalchemy.Column('time', sqlalchemy.TIME),
                            sqlalchemy.Column('comment', sqlalchemy.TEXT)
                            )


def load_user_info(user):
    user_info = {}

    query = USERS_TABLE.select().where(USERS_TABLE.c.username == user)
    result = conn.execute(query)
    row = result.fetchone()
    if row:
        user_info['user_id'] = row['user_id']
        user_info['username'] = row['username']
        user_info['firstname'] = row['firstname'] if 'firstname' in row else ''
        user_info['lastname'] = row['lastname'] if 'lastname' in row else ''
        user_info['email'] = row['email']
    return user_info


def save_tourist_spot(tourist_spot):
    if tourist_spot and tourist_spot.destinationName:
        if tourist_spot.geocode:
            lat = tourist_spot.geocode.get('lat', None)
            lng = tourist_spot.geocode.get('lng', None)
        else:
            lat = None
            lng = None
        query = TOURIST_SPOT_TABLE.insert().values(google_id=tourist_spot.destinationID,
                                                   name=tourist_spot.destinationName,
                                                   latitude=lat,
                                                   longitude=lng,
                                                   rating=tourist_spot.rating,
                                                   address=tourist_spot.address,
                                                   image_link=tourist_spot.image_link
                                                   ).returning(TOURIST_SPOT_TABLE.c.tourist_spot_id)
        result = conn.execute(query)
        return result.fetchone()[0]
    return None

def load_tourist_spot(ts_id=None, google_id=None):
    if ts_id is not None:
        query = TOURIST_SPOT_TABLE.select().where(TOURIST_SPOT_TABLE.c.tourist_spot_id == int(ts_id))
    elif google_id is not None:
        query = TOURIST_SPOT_TABLE.select().where(TOURIST_SPOT_TABLE.c.google_id == str(google_id))
    else:
        return None
    result = conn.execute(query).fetchone()
    #print result
    if result:
        return TouristSpot(db_spot=result)


def save_itinerary(user, itinerary):
    query = USERS_TABLE.select().where(USERS_TABLE.c.username == user)
    result = conn.execute(query)
    row = result.fetchone()
    if row:
        user_id = row['user_id']
        query = ITINERARY_TABLE.insert().values(city=itinerary.city).returning(ITINERARY_TABLE.c.itinerary_id)

        result = conn.execute(query)
        itinerary_id = result.fetchone()[0]
        query = USER_ITINERARIES.insert().values(user_id=user_id, itinerary_id=itinerary_id, privilege=1)
        conn.execute(query)

        ordernum = 0
        day_num = 1
        for day in itinerary.touristSpots:
            for t_spot in day:
                ordernum += 1
                query = TOURIST_SPOT_TABLE.select().where(and_(TOURIST_SPOT_TABLE.c.google_id == t_spot.destinationID, TOURIST_SPOT_TABLE.c.name == t_spot.destinationName))
                result = conn.execute(query)

                if not result:
                    save_tourist_spot(t_spot)
                    query = TOURIST_SPOT_TABLE.select().where(and_(TOURIST_SPOT_TABLE.c.google_id == t_spot.destinationID,
                    TOURIST_SPOT_TABLE.c.name == t_spot.destinationName))
                    result = conn.execute(query)

                tourist_spot_id = result.fetchone()['tourist_spot_id']
                time_to_next_dest = None

                if t_spot.next_dest_time:
                    time_to_next_dest = t_spot.next_dest_time
                
                query = ITINERARY_SPOTS.insert().values(itinerary_id=itinerary_id,
                                                        tourist_spot_id=tourist_spot_id,
                                                        destination_num=ordernum,
                                                        time_to_next_dest=time_to_next_dest,
                                                        day_num=day_num,
                                                        )
                conn.execute(query)
            day_num += 1
        return itinerary_id

def load_user_itinerary_info(user):
    itineraries = {}
    query = USERS_TABLE.select().where(USERS_TABLE.c.username == user)
    result = conn.execute(query)
    user_row = result.fetchone()

    if user_row:
        user_id = user_row['user_id']
        query = USER_ITINERARIES.select().where(USER_ITINERARIES.c.user_id == user_id)
        result = conn.execute(query)
        itinerary_rows = result.fetchall()
        for itinerary_row in itinerary_rows:
            query = ITINERARY_TABLE.select().where(ITINERARY_TABLE.c.itinerary_id == itinerary_row['itinerary_id'])
            result = conn.execute(query)
            city = result.fetchone()['city']
            #itinerary = load_itinerary(itinerary_row['itinerary_id'])
            itinerary = Itinerary.Itinerary(city, db_id=itinerary_row['itinerary_id'])
            itinerary.id = itinerary_row['itinerary_id']
            itineraries[itinerary_row['itinerary_id']] = {'city': city, 'itinerary_info': itinerary}

    return itineraries


def get_user_itineraries(user):
    itineraries = []
    query = USERS_TABLE.select().where(USERS_TABLE.c.username == user)
    result = conn.execute(query)
    user_row = result.fetchone()

    if user_row:
        user_id = user_row['user_id']
        query = USER_ITINERARIES.select().where(USER_ITINERARIES.c.user_id == user_id)
        result = conn.execute(query)
        itinerary_rows = result.fetchall()
        for itinerary_row in itinerary_rows:
            query = ITINERARY_TABLE.select().where(ITINERARY_TABLE.c.itinerary_id == itinerary_row['itinerary_id'])
            result = conn.execute(query)
            city = result.fetchone()['city']
            
            all_users = []
            query = USER_ITINERARIES.select().where(USER_ITINERARIES.c.itinerary_id == itinerary_row['itinerary_id'])
            result = conn.execute(query)
            users = result.fetchall()  
            for user_in_itinerary in users:
                query = USERS_TABLE.select().where(USERS_TABLE.c.user_id == user_in_itinerary['user_id'])
                result = conn.execute(query)
                user_row = result.fetchone()
                if user_in_itinerary['privilege'] == 1:
                    manager = user_row['username']
                else:
                    all_users.append(user_row['username'])

            itineraries.append({'city': city, 'itinerary_id': itinerary_row['itinerary_id'], 'users': all_users, 'manager' : manager})
    return itineraries

def load_itinerary(itinerary_id):
    days = []
    query = ITINERARY_SPOTS.select().where(ITINERARY_SPOTS.c.itinerary_id == itinerary_id).group_by(ITINERARY_SPOTS.c.day_num, ITINERARY_SPOTS.c.itinerary_id, ITINERARY_SPOTS.c.tourist_spot_id, ITINERARY_SPOTS.c.time_to_next_dest ).order_by(asc(ITINERARY_SPOTS.c.destination_num))
    result = conn.execute(query)
    itinerary_rows = result.fetchall()
    if itinerary_rows:
      cur_day = itinerary_rows[0]['day_num']
      tourist_spots = []
      for row in itinerary_rows:
          if cur_day != row['day_num']:
            days.append(tourist_spots)
            tourist_spots = []
            cur_day = row['day_num']

          query = TOURIST_SPOT_TABLE.select().where(TOURIST_SPOT_TABLE.c.tourist_spot_id == row['tourist_spot_id'])
          result = conn.execute(query)
          tourist_spot_row = result.fetchone()

          if tourist_spot_row:
            tourist_spot_dict = dict(tourist_spot_row.items())
            tourist_spot_dict['time_to_next_dest'] = row['time_to_next_dest']
            tourist_spots.append(TouristSpot(db_spot=tourist_spot_dict))

      days.append(tourist_spots)
    return days

def delete_itinerary(itinerary_id):
    query = COMMENTS.delete().where(COMMENTS.c.itinerary_id == itinerary_id)
    conn.execute(query)
    query = ITINERARY_SPOTS.delete().where(ITINERARY_SPOTS.c.itinerary_id == itinerary_id)
    conn.execute(query)
    query = USER_ITINERARIES.delete().where(USER_ITINERARIES.c.itinerary_id == itinerary_id)
    conn.execute(query)
    query = ITINERARY_TABLE.delete().where(ITINERARY_TABLE.c.itinerary_id == itinerary_id)
    conn.execute(query)

def add_user(user, itinerary_id):
    query = USERS_TABLE.select().where(USERS_TABLE.c.username == user)
    #print user
    result = conn.execute(query)
    user_row = result.fetchone()

    if user_row:
        user_id = user_row['user_id']
        query = USER_ITINERARIES.select().where(and_(USER_ITINERARIES.c.itinerary_id == itinerary_id, USER_ITINERARIES.c.user_id == user_id))
        result = conn.execute(query)
        row = result.fetchone()
        if not row:
          query = USER_ITINERARIES.insert().values(itinerary_id=itinerary_id,
                                               user_id=user_id, privilege=2)
          conn.execute(query)
    else:
        return 'User does not exist' 
    return None

def remove_user(user, itinerary_id):
    query = USERS_TABLE.select().where(USERS_TABLE.c.username == user)
    result = conn.execute(query)
    user_row = result.fetchone()
    if user_row:
        user_id = user_row['user_id']
        query = USER_ITINERARIES.delete().where(and_(USER_ITINERARIES.c.user_id == user_id, USER_ITINERARIES.c.itinerary_id == itinerary_id, USER_ITINERARIES.c.privilege == 2))
        conn.execute(query)
    else:
        return 'User does not exist'
    return None

def add_comment(user, itinerary_id, comment):
    query = USERS_TABLE.select().where(USERS_TABLE.c.username == user)
    result = conn.execute(query)
    user_row = result.fetchone()
    if user_row:
        try:
            user_id = user_row['user_id']
            query = COMMENTS.insert().values(itinerary_id=itinerary_id, user_id=user_id, comment=comment, time=datetime.datetime.now())
            conn.execute(query)
        except:
            return 'Error executing query'
    else:
        return 'User does not exist' 
    return None

def get_itinerary_comments(itinerary_id):
    query = COMMENTS.select().where(COMMENTS.c.itinerary_id == itinerary_id).order_by(asc(COMMENTS.c.time))
    result = conn.execute(query)
    rows = result.fetchall()
    if rows:
        comments = []
        for row in rows:
            comment = {}
            query = USERS_TABLE.select().where(USERS_TABLE.c.user_id == row['user_id'])
            result = conn.execute(query)
            user_row = result.fetchone()
            if user_row:
                comment['username'] = user_row['username']
            comment['comment'] = row['comment']
            comment['time'] = row['time']
            comments.append(comment)
        return comments
    return None
