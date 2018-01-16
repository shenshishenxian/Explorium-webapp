from Itinerary import Itinerary
from flask import Flask, render_template, abort, jsonify, request, g, session, redirect, flash, url_for, request
import sqlalchemy
from sqlalchemy import and_, or_
from flask import Flask, request, render_template, g, redirect, Response
import traceback
import ItineraryService
import ExploriumDbApi
from TouristSpot import TouristSpot
import os, time, re
import utils
import datetime
import requests
import json
import sys  

from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

template_dir = os.path.abspath('../templates')
static_dir = os.path.abspath('../static')

DATABASEURI = "postgresql://fortytwo:explorium-COMS4156@coms4156.cf4dw5ld7jgf.us-east-2.rds.amazonaws.com:5432/Explorium"
engine = sqlalchemy.create_engine(DATABASEURI)

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'secret!'
DAY_LIMIT = 7

@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        #print("problem connecting to database")
        traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

@app.route("/")
@app.route("/index")
def index():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))
    return render_template('index.html', this_username=session['username'], show_what="Welcome!", result_info_list='')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    ref = request
    if request.method == 'POST':
        try:
            username = request.form.get('user_username')
            email = request.form.get('user_email')
            password = utils.hash_password(request.form.get('user_password'))
            firstname = request.form.get('user_firstname')
            lastname = request.form.get('user_lastname')
            repeat_password = utils.hash_password(request.form.get('user_repeat_password'))
            if password != repeat_password:
                error = " Passwords do not match ! "
                return render_template('signup.html', error=error)

            if not utils.valid_username(username):
                traceback.print_exc()
                error = " Username is already taken "
                return render_template('signup.html', error=error)

            if not utils.valid_email(email):
                traceback.print_exc()
                p = re.compile('[aA0-zZ9$]+@[aA0-zZ9]+.[a-z]+')
                if p.match(email) is None:
                    error = " Email is already taken "
                else:
                    error = " Invalid Email"
                return render_template('signup.html', error=error)

            session['username'] = username
            # session['password'] = password
            query = ExploriumDbApi.USERS_TABLE.insert().values(username=username, password=password, email=email,
                                                               firstname=firstname, lastname=lastname)
            ExploriumDbApi.conn.execute(query)

            return render_template('index.html', this_username=session['username'], show_what="Welcome!",
                                   result_info_list='')
        except Exception as e:
            render_template('signup.html', error='Invalid Input')


    return render_template('signup.html')


@app.route('/signin_as_a_guest', methods=['GET', 'POST'])
def signin_as_guest():
    session['username'] = 'guest'
    session['password'] = ' '
    return redirect(url_for('index'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    ref = request
    error = None
    if request.method == 'POST':
        try:
            username = request.form.get('user_username')
            password = utils.hash_password(request.form.get('user_password'))

            query = ExploriumDbApi.USERS_TABLE.select().where(and_(ExploriumDbApi.USERS_TABLE.c.username == username,
                                                                   ExploriumDbApi.USERS_TABLE.c.password == password))

            result = ExploriumDbApi.conn.execute(query)
            if not result.fetchone():
                error = "Invalid username or password"
                flash('Invalid username or password')
                return render_template('signin.html', error=error)

            flash('You have successfully logged in')
            session['username'] = username
            session['password'] = password
            return redirect(url_for('index'))
        except:
            flash('Invalid username or password')
            return render_template('signin.html')
    return render_template('signin.html')


@app.route('/profile')
def view_profile():
    if 'username' not in session:
        return redirect(url_for('signin'))
    if session['username'] == 'guest':
        return redirect(url_for('index'))
    userinfo = ExploriumDbApi.load_user_info(session['username'])
    return render_template('profile.html', this_username=session['username'], user_info=userinfo)


@app.route('/profile-edit', methods=["GET", "POST"])
def edit_profile():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))
    if session['username'] == 'guest':
        return redirect(url_for('index'))

    if request.method == 'GET':
        if 'username' not in session:
            return redirect(url_for('signin'))
        userinfo = ExploriumDbApi.load_user_info(session['username'])
        error = ""

        return render_template('profile-edit.html', this_username=session['username'], user_info=userinfo, error=error)
    if request.method == "POST":
        try:
            if 'username' not in session:
                return redirect(url_for('signin'))
            firstname = request.form.get('user-firstname')
            lastname = request.form.get('user-lastname')
            email = request.form.get('user-email')
            username = request.form.get('user-username')

            userinfo = ExploriumDbApi.load_user_info(session['username'])

            if not firstname or not lastname or not email or not username:
                traceback.print_exc()
                error = " Fields cannot be empty. "
                return render_template('profile-edit.html', this_username=session['username'], user_info=userinfo,
                                       error=error)
            if not utils.valid_username(username) and username != userinfo['username']:
                error = " Username is already taken "
                return render_template('profile-edit.html', this_username=session['username'], user_info=userinfo,
                                           error=error)
            if not utils.valid_email(email) and email != userinfo['email']:
                p = re.compile('[aA0-zZ9$]+@[aA0-zZ9]+.[a-z]+')
                if p.match(email) is None:
                    error = " Email is already taken "
                else:
                    error = " Invalid Email"
                return render_template('profile-edit.html', this_username=session['username'], user_info=userinfo,
                                       error=error)

            session['username'] = username
            if request.form.get('user-password'):
                password = utils.hash_password(request.form.get('user-password'))
                query = ExploriumDbApi.USERS_TABLE.update().where(
                    ExploriumDbApi.USERS_TABLE.c.user_id == userinfo['user_id']).values(firstname=firstname, lastname=lastname,
                                                                                        username=username, email=email,
                                                                                        password=password)
            else:
                query = ExploriumDbApi.USERS_TABLE.update().where(
                    ExploriumDbApi.USERS_TABLE.c.user_id == userinfo['user_id']).values(firstname=firstname, lastname=lastname,
                                                                                        username=username, email=email)

            ExploriumDbApi.conn.execute(query)

            userinfo = ExploriumDbApi.load_user_info(session['username'])

            return render_template('profile.html', this_username=session['username'], user_info=userinfo)
        except:
            userinfo = ExploriumDbApi.load_user_info(session['username'])
            error = "Invalid Input"

            return render_template('profile-edit.html', this_username=session['username'], user_info=userinfo,
                                   error=error)

@app.route('/logout')
def logout():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))
    flash('You were logged out')
    session.pop('username', None)
    return redirect(url_for('signin'))

@app.route('/save', methods=['GET','POST'])
def save():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))
    
    if 'current_view_itinerary' in session and session['current_view_itinerary']['db_id'] is None:
        itinerary = session['current_view_itinerary']
        cur_itinerary = Itinerary(itinerary['city'], itinerary=itinerary)
        db_id = ExploriumDbApi.save_itinerary(session['username'], cur_itinerary)
        cur_itinerary.db_id = db_id
        session['current_view_itinerary'] = cur_itinerary.to_dict()
        return redirect(url_for('get_itinerary_by_id', db_id=session['current_view_itinerary']['db_id']))
        #return render_template('show_itinerary.html', this_username=session['username'], city=cur_itinerary.city, itinerary=session['current_view_itinerary'], error="")
    return render_template('show_itinerary.html', this_username=session['username'], itinerary=session['current_view_itinerary'], error="")
    #add error case here
@app.route('/delete_itinerary/<db_id>', methods=['GET','POST'])
def delete_itinerary(db_id):
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))

    query = ExploriumDbApi.USERS_TABLE.select().where(ExploriumDbApi.USERS_TABLE.c.username == session['username'])
    user_row = ExploriumDbApi.conn.execute(query).fetchone()
    if user_row:
        query = ExploriumDbApi.USER_ITINERARIES.select().where(and_(ExploriumDbApi.USER_ITINERARIES.c.user_id == user_row['user_id'], ExploriumDbApi.USER_ITINERARIES.c.itinerary_id == db_id))
        result = ExploriumDbApi.conn.execute(query)
        itinerary_row = result.fetchone()
        if itinerary_row and itinerary_row['privilege'] == 1:
            ExploriumDbApi.delete_itinerary(db_id)
        return redirect(url_for('view_itineraries'))
    return redirect(url_for('signin'))

@app.route('/add_spot/<t_id>', methods=['GET', 'POST'])
def add_tourist_spot(t_id):
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))
    it_id = request.args.get('itinerary')
    query = ExploriumDbApi.ITINERARY_TABLE.select().where(ExploriumDbApi.ITINERARY_TABLE.c.itinerary_id == it_id)
    result = ExploriumDbApi.conn.execute(query).fetchone()
    if result:   
        cur_itinerary = Itinerary(result['city'], db_id=it_id)
        cur_itinerary.add_spot(ExploriumDbApi.load_tourist_spot(ts_id=t_id))
        new_db_id = ExploriumDbApi.save_itinerary(session['username'], cur_itinerary)
        cur_itinerary.db_id = new_db_id
        query = ExploriumDbApi.COMMENTS.update().where(ExploriumDbApi.COMMENTS.c.itinerary_id == it_id).values(itinerary_id=new_db_id)
        ExploriumDbApi.conn.execute(query)
        cur_itinerary.db_id = new_db_id
        ExploriumDbApi.delete_itinerary(it_id)
    return redirect(url_for('spotdetail', dest_id=t_id))

@app.route('/delete_spot/<t_id>', methods=['GET', 'POST'])
def delete_tourist_spot(t_id):
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))

    if 'current_view_itinerary' in session:
        if session['current_view_itinerary']['db_id'] is not None:
            cur_itinerary = Itinerary(session['current_view_itinerary']['city'], db_id =session['current_view_itinerary']['db_id'])
            cur_itinerary.del_spot(ExploriumDbApi.load_tourist_spot(ts_id=t_id))
            new_db_id = ExploriumDbApi.save_itinerary(session['username'], cur_itinerary)
            query = ExploriumDbApi.COMMENTS.update().where(ExploriumDbApi.COMMENTS.c.itinerary_id == session['current_view_itinerary']['db_id']).values(itinerary_id=new_db_id)
            ExploriumDbApi.conn.execute(query)
            cur_itinerary.db_id = new_db_id
            ExploriumDbApi.delete_itinerary(session['current_view_itinerary']['db_id'])
            session['current_view_itinerary'] = cur_itinerary.to_dict() 
        return render_template('show_itinerary.html', this_username=session['username'], city=session['current_view_itinerary']['city'], itinerary=session['current_view_itinerary'], error="")
    return render_template('index.html', this_username=session['username'], show_what="Welcome!", result_info_list='')

@app.route('/add_user/<db_id>', methods=['GET', 'POST'])
def add_user_itinerary(db_id):
    new_user = request.form.get('user')
    if db_id != None:
        result = ExploriumDbApi.add_user(new_user, db_id)
    return redirect(url_for('view_itineraries'))

@app.route('/remove_user/<db_id>', methods=['GET', 'POST'])
def remove_user_itinerary(db_id):
    user = request.form.get('user')
    if db_id != None:
        result = ExploriumDbApi.remove_user(user, db_id)
    return redirect(url_for('view_itineraries'))

@app.route('/regenerate/<city>', methods=['GET', 'POST'])
def regenerate(city):
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))

    old = session['current_view_itinerary']
    try:
        preferences = dict()
        preferences['time_spent'] = request.form.get('days')
        if int(preferences['time_spent']) > DAY_LIMIT:
            preferences['time_spent'] = DAY_LIMIT
        preferences['max_price'] = request.form.get('price')
        itinerary = Itinerary(city, preferences=preferences)

        if 'db_id' in session['current_view_itinerary']:
            new_db_id = ExploriumDbApi.save_itinerary(session['username'], itinerary)
            itinerary.db_id = new_db_id
            query = ExploriumDbApi.COMMENTS.update().where(ExploriumDbApi.COMMENTS.c.itinerary_id == session['current_view_itinerary']['db_id']).values(itinerary_id=new_db_id)
            ExploriumDbApi.conn.execute(query)
            ExploriumDbApi.delete_itinerary(session['current_view_itinerary']['db_id'])
            session['current_view_itinerary'] = itinerary.to_dict()
            return redirect(url_for('get_itinerary_by_id', db_id=session['current_view_itinerary']['db_id']))
        return render_template('show_itinerary.html', this_username=session['username'], city=session['current_view_itinerary']['city'], itinerary=itinerary.to_dict(), error="")
    except Exception as e:
        #print e
        session['current_view_itinerary'] = old
        if 'username' not in session or 'password' not in session:
            return redirect(url_for('signin'))
        return render_template('show_itinerary.html', this_username=session['username'], city=session['current_view_itinerary']['city'], itinerary=session['current_view_itinerary'], error="")
        
@app.route('/get_comment', methods=['GET', 'POST'])
def get_comment():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))
    if request.method == "POST":    
        if 'current_view_itinerary' in session:
            commentText = request.form.get('comment')
            if session['current_view_itinerary']['db_id'] is not None: 
                ExploriumDbApi.add_comment(session['username'], session['current_view_itinerary']['db_id'], commentText)
                return redirect(url_for('get_itinerary_by_id', db_id=session['current_view_itinerary']['db_id']))
            # comment = session['current_view_itinerary']['comments']
            # if not comment:
            #     comment = []
            # comments = {}
            # comments['username'] = session['username']
            # comments['comment'] = commentText
            # comments['time'] = datetime.datetime.now()
            # comment.append(comments)
            # session['current_view_itinerary']['comments'] = comment
            # print session['current_view_itinerary']
            return render_template('show_itinerary.html', this_username=session['username'], itinerary=session['current_view_itinerary'], error="Save itinerary before commenting.")
            

@app.route('/view_itineraries')
def view_itineraries():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))
    if session['username'] == 'guest':
        return redirect(url_for('index'))
    if request.method == 'GET':
        if 'username' not in session:
            return redirect(url_for('signin'))
        itineraries = ExploriumDbApi.get_user_itineraries(session['username'])
        return render_template('view_itineraries.html', this_username = session['username'], itineraries=itineraries)

@app.route('/search_city', methods = ['GET','POST'])
def search_city():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))
    try:
        city = request.form.get('search_box')
        preferences = dict()
        preferences['time_spent'] = 2
        places_list = ItineraryService.generate_tourist_spot_list(city, preferences=preferences)
        tourist_spot_list = []
        all_spots = []
        for spot in places_list:
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
        for t_spot in tourist_spot_list:
            all_spots.append(t_spot.to_dict())
        all_spots = json.dumps(all_spots)
        return render_template('index.html', this_username=session['username'],
                               show_what="Search Results: " + city,
                               result_info_list=all_spots)
    except Exception as e:
        return render_template('index.html', this_username=session['username'], show_what="Welcome!",
                               result_info_list='')

@app.route('/itinerary/<db_id>', methods=['GET', 'POST'])
def get_itinerary_by_id(db_id):
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))

    query = ExploriumDbApi.ITINERARY_TABLE.select().where(ExploriumDbApi.ITINERARY_TABLE.c.itinerary_id == db_id)
    result = ExploriumDbApi.conn.execute(query).fetchone()

    if result:
        itinerary = Itinerary(result['city'], db_id=db_id)
        session['current_view_itinerary'] = itinerary.to_dict()
        return render_template('show_itinerary.html', this_username=session['username'], itinerary=session['current_view_itinerary'], error="")
    return redirect(url_for('view_itineraries'))


@app.route('/route', methods=['GET', 'POST'])
def route():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('signin'))
    if request.method == 'GET':
        return render_template('route.html', this_username=session['username'], error="")
    else:
        try:
            preferences = dict()
            preferences['time_spent'] = request.form.get('rangeInput')
            if int(preferences['time_spent']) > DAY_LIMIT:
                preferences['time_spent'] = DAY_LIMIT 
            preferences['max_price'] = request.form.get('price')
            city = request.form.get('city')
            preferences['types'] = request.form.getlist('t_spot')
            itinerary = Itinerary(city, preferences=preferences)
            session['current_view_itinerary'] = itinerary.to_dict()

            return render_template('show_itinerary.html', this_username=session['username'], itinerary=session['current_view_itinerary'], error="")
        except Exception as e:
            #print e
            if 'username' not in session or 'password' not in session:
                return redirect(url_for('signin'))
            return render_template('index.html', this_username=session['username'], show_what="Welcome!",
                                   result_info_list='')

@app.route('/spotdetail/<dest_id>',methods=["GET"])
def spotdetail(dest_id):
    if 'username' not in session:
        return redirect(url_for('signin'))
 
    spot_detail = ExploriumDbApi.load_tourist_spot(ts_id=dest_id)
    spot_detail2 = spot_detail.to_dict()

    spot_detail2['geocode']['lat'] = float(spot_detail2['geocode']['lat'])
    spot_detail2['geocode']['lng'] = float(spot_detail2['geocode']['lng'])

    try:
        itineraries = ExploriumDbApi.get_user_itineraries(session['username'])
        url = 'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles='+spot_detail2['destinationName']
        string = requests.get(url)
        result = string.json()["query"]["pages"]
        for item in result:
            summary = result[item]["extract"].encode('utf-8')
                
        reload(sys)  
        sys.setdefaultencoding('utf8')
    except Exception as e:
        summary = 'Not enough information on this location currently!'
    return render_template('spotdetail.html', this_username = session['username'], spot_info=spot_detail2, intro=summary, itineraries=itineraries)


if __name__ == '__main__':
    app.run(debug=True)
      #app.run(host='0.0.0.0', port=80)
