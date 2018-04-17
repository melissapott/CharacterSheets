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
	person.status = request.form['status']
        session.add(person)
        session.commit()
        flash('Person %s has been edited!' % person.fname)

        return redirect(url_for ('home'))

    else:
	return render_template('editperson.html', person=person)

if __name__ == '__main__':
    app.secret_key = 'blahblahblah'
    app.debug = True
    app.run(host='0.0.0', port=8000)
