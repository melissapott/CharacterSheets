from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import psycopg2
from database_setup import Base, Person, Character, Race, Faction, Ability, Attribute

# Set up a connection to the database
engine = create_engine('postgresql://charsheet:4ab62xxc@localhost/charsheet')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def addAbilities():
    Combat = ['Athletics','Brawl','Dodge','Melee','Ranged']
    Knowledge = ['Academics','Enigmas','Science','Technology']
    Perception = ['Alertness','Awareness','Investigation','Stealth']
    Practicality = ['Crafts','Medicine','Security','Streetwise']
    Social = ['Empathy','Expression','Intimidation','Persuasuion','Subterfuge']
    Networking = ['Bureaucracy','Finance','High Society','Politics']

    for i in Combat:
        skill = Ability(type='Combat', name=i)
        session.add(skill)
        session.commit()

    for i in Knowledge:
        skill = Ability(type='Knowledge', name=i)
        session.add(skill)
        session.commit()

    for i in Perception:
        skill = Ability(type='Perception', name=i)
        session.add(skill)
        session.commit()

    for i in Practicality:
        skill = Ability(type='Practicality', name=i)
        session.add(skill)
        session.commit()

    for i in Social:
        skill = Ability(type='Social', name=i)
        session.add(skill)
        session.commit()

    for i in Networking:
        skill = Ability(type='Networking', name=i)
        session.add(skill)
        session.commit()

def addAttributes():
    attr = ['Strength','Dexterity','Stamina','Charisma','Manipulation','Appearance','Perception','Intelligence','Wits']

    for i in attr:
        skill = Attribute(name=i)
        session.add(skill)
        session.commit()

addAbilities()
addAttributes()
