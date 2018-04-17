from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import psycopg2

Base = declarative_base()

# define database tables
class Person(Base):
	__tablename__ = 'person'
	id = Column(Integer, primary_key = True)
	fname = Column(String(250), nullable = False)
	lname = Column(String(250), nullable = False)
	email = Column(String(250))
	status = Column(String(10))

	@property
	def serialize(self):
	#this will be used for returning a JSON object
		return {
			'id': self.id,
			'name' : self.name,
			'email' : self.email,
			'status' : self.status
		}

class Character(Base):
	__tablename__ = 'character'
	id = Column(Integer, primary_key = True)
	person_id = Column(Integer, ForeignKey('person.id'))
	name = Column(String(250), nullable = False)
	race = Column(Integer, ForeignKey('race.id'))
	concept = Column(String(250), nullable = True)


class Race(Base):
	__tablename__ = 'race'
	id = Column(Integer, primary_key = True)
	name = Column(String(100), nullable = False)

	@property
	def serialize(self):
		return {
			'id' : self.id,
			'name' : self.name
		}

class Faction(Base):
	__tablename__ = 'faction'
	id = Column(Integer, primary_key = True)
	race_id = Column(Integer, ForeignKey('race.id'))
	name = Column(String(100), nullable = False)

	@property
	def serialize(self):
		return {
			'id' : self.id,
			'race_id' : self.race_id,
			'name' : self.name
		}




engine = create_engine('postgresql://charsheet:4ab62xxc@localhost/charsheet')

Base.metadata.create_all(engine)
