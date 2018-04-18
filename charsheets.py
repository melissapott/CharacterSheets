# Import required libraries
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask import make_response, send_file, flash
# we're already using the word session for db session
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Person, Character, Race, Faction
import random, string, json
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2, requests, os, sys, psycopg2
from werkzeug.utils import secure_filename
from flask import send_from_directory

app = Flask(__name__)



# Set up a connection to the database
engine = create_engine('postgresql://charsheet:4ab62xxc@localhost/charsheet')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show the main page
@app.route('/')
def home():
    return render_template('home.html')


# Add users page
@app.route('/person/add', methods=['GET', 'POST'])
def addPerson():
    #TO DO:  restrict this route for anyone other than logged in users Staff or higher
    if request.method == 'POST':
        newPerson = Person(fname=request.form['fname'], lname=request.form['lname'], email=request.form['email'], status=request.form['status'])
        session.add(newPerson)
        session.commit()
        flash("New Person %s has been created!" % newPerson.fname)
        return redirect(url_for ('home'))
    else:
        return render_template('addperson.html')

# List users page
@app.route('/person/list', methods=['GET'])
def listPerson():
    person = session.query(Person)
    return render_template('listperson.html', person=person)

# Edit users page
@app.route('/person/<int:id>/edit', methods=['GET', 'POST'])
def editPerson(id):

    #TO DO: restrict this route for anyone other than logged in users
    person = session.query(Person).filter_by(id=id).one()

    if request.method == 'POST':
        person.fname = request.form['fname']
        person.lname = request.form['lname']
        person.email = request.form['email']
	session.add(person)
        session.commit()
        flash('Person %s has been edited!' % person.fname)

        return redirect(url_for ('home'))

    else:
	return render_template('editperson.html', person=person)

# code for dealing with logging users in and out
# from Udacity Authorization and Authentication class

def getUserID(email):
    try:
        user = session.query(Person).filter_by(email=email).one()
        return user.id
    except:
        return None


def createUser(login_session):
    newUser = Person(name=login_session[
                   'username'], email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(Person).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Person).filter_by(user_id=user_id).one()
    return user

# get the Google API client information
APP_PATH = '/var/www/CharacterSheets/'
CLIENT_ID = json.loads(
    open(APP_PATH + 'client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "CrimsonAccord"


@app.route('/login')
def showLogin():
    # create a random string to be used as a CSRF token - we'll check it again
    # later and if it doesn't match, there may have been a hijack
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Google Login
@app.route('/gconnect', methods=['POST'])
def gConnect():
    # Validate state token - check for hijack
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code - obtained from javascript in login.html
    code = request.data

    try:
        # exchange the authorization code for a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/Catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except:
        response = make_response(json.dumps('authorization unsucessful'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = credentials.access_token

    # check that the access token we got is valid
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps("result.get('error')"), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # is the access token issued for the intended user?
    g_id = credentials.id_token['sub']
    if result['user_id'] != g_id:
        response = make_response(json.dumps(
            "Token ID doesn't match User"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # is the access token valid for this application?
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "token not valid for this app"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # is the user already logged in?
    stored_credentials = login_session.get('credentials')
    stored_g_id = login_session.get('g_id')
    if stored_credentials is not None and g_id == stored_g_id:
        response = make_response(json.dumps('user is already logged in'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # everything checks out, so save the credentials to the session
    login_session['credentials'] = credentials.access_token
    login_session['g_id'] = g_id

    # get the user info from the Google API
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    reply = requests.get(userinfo_url, params=params)
    data = reply.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # does the user already exist in the database?  If not, create a new user
    # entry
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h2>Welcome, '
    output += login_session['username']
    output += '!</h2>'
    flash("You are now logged in as %s" % login_session['username'])
    return output

# Facebook Login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    # Exchange client token for long-lived server-side token

    app_id = json.loads(open('/var/www/Catalog/fb_client_secrets.json',
                             'r').read())['web']['app_id']
    app_secret = json.loads(open('/var/www/Catalog/fb_client_secrets.json',
                                 'r').read())['web']['app_secret']

    url = ('https://graph.facebook.com/v2.9/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
           '&fb_exchange_token=%s' % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)


    # Extract the access token from response
    token = 'access_token=' + data['access_token']
 
    # use token to get user infor from API
    url = 'https://graph.facebook.com/v2.9/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['facebook_id'] = data["id"]
    login_session['email'] = data['email']

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    flash("You are now logged in as %s" % login_session['username'])
    return output




# Disconnect from either Facebook or Google
@app.route('/logout')
def logout():
    if login_session:
        if login_session['provider'] == 'google':
            response = gdisconnect()
        elif login_session['provider'] == 'facebook':
            response = fbdisconnect()
    else:
        response = "user is not logged in"
    flash(response)
    return redirect(url_for('home'))

# Facebook Disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    login_session.clear()
    return "you have been logged out"

# Google Disconnect
@app.route("/gdisconnect")
def gdisconnect():
    credentials = login_session.get('credentials')

    if credentials is None:
        response = make_response(json.dumps(
            'Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session
        login_session.clear()
        response = "Successfully Disconnected"
        return response
    else:
        # an error where the given token was invalid
        response = "Error logging out"
        return response

if __name__ == '__main__':
    app.secret_key = 'blahblahblah'
    app.debug = True
    app.run(host='0.0.0', port=8000)
