# Import required libraries
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask import make_response, send_file, flash
# we're already using the word session for db session
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Person, Character, Race, Faction


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

# Page to log users in
@app.route('/login')
def showLogin():
    # add code to log in user
    pass
# Logout page
@app.route('/logout')
def logout():
    # add code here to log out users
    pass



if __name__ == '__main__':
    app.secret_key = 'blahblahblah'
    app.debug = True
    app.run(host='0.0.0', port=8000)
