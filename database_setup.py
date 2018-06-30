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

class Race(Base):
	__tablename__ = 'race'
	id = Column(Integer, primary_key = True)
	name = Column(String(100), nullable = False)

class Character(Base):
	__tablename__ = 'character'
	id = Column(Integer, primary_key = True)
	person_id = Column(Integer, ForeignKey('person.id'))
	name = Column(String(250), nullable = False)
	race_id = Column(Integer, ForeignKey('race.id'))
	concept = Column(String(250), nullable = True)
	person = relationship(Person)
	race = relationship(Race)

class Faction(Base):
	__tablename__ = 'faction'
	id = Column(Integer, primary_key = True)
	race_id = Column(Integer, ForeignKey('race.id'))
	name = Column(String(100), nullable = False)
	race = relationship(Race)

class Ability(Base):
	__tablename__ = 'ability'
	id = Column(Integer, primary_key = True)
	type = Column(String(100), nullable = False)
	name = Column(String(100), nullable = False)


class Attribute(Base):
	__tablename__ = 'attribute'
	id = Column(Integer, primary_key = True)
	name = Column(String(100), nullable = False)


engine = create_engine('postgresql://charsheet:4ab62xxc@localhost/charsheet')

Base.metadata.create_all(engine)
