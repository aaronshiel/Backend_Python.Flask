from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
import os
from flask_marshmallow import Marshmallow
from Utilities import database_login_utilities
from socket import gethostname

app = Flask(__name__)
# grab the path for this application to store DB
basedir = os.path.abspath(os.path.dirname(__file__))
# configuring database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'Database.db')
db = SQLAlchemy(app)
marsh = Marshmallow(app)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('database created!')


# Called when a user is trying to create an account
# request must have params of username and password
@app.route('/create_account', methods=['POST'])
def db_create_user():
    if request.is_json:
        username = request.json['username']
        password = request.json['password']
    else:
        username = request.form['username']
        password = request.form['password']
    return database_login_utilities.db_create_user(db=db, username=username, password=password)


# Called when a user is trying to access an already created planner
# request must have params of planner_id
@app.route('/get_planner_info', methods=['POST'])
def get_planner_info():
    if request.is_json:
        planner_id = request.json['planner_id']
    else:
        planner_id = request.form['planner_id']
    return database_login_utilities.get_planner_info(db=db, planner_id=planner_id)


# Called when a planner is opened
# Accesses single event info
# request must have params of event_id
@app.route('/get_event_info', methods=['POST'])
def get_event_info():
    if request.is_json:
        event_id = request.json['event_id']
    else:
        event_id = request.form['event_id']
    return database_login_utilities.get_event_info(db=db, event_id=event_id)


# Called when a user is trying to log in
# request must have params of username and password
@app.route('/login_account', methods=['POST'])
def db_login():
    if request.is_json:
        username = request.json['username']
        password = request.json['password']
    else:
        username = request.form['username']
        password = request.form['password']
    return database_login_utilities.db_login_user(db=db, username=username, password=password)


# Called when a user is creating a new event inside a planner
# Request must have params of date, description, username, and plannerID
@app.route('/new_event', methods=['POST'])
def create_new_event():
    if request.is_json:
        date = request.json['date']
        description = request.json['description']
        username = request.json['username']
        plannerID = request.json['plannerID']
    else:
        date = request.form['date']
        description = request.form['description']
        username = request.form['username']
        plannerID = request.form['plannerID']
    return database_login_utilities.db_create_event(db=db, date=date, description=description, username=username, plannerID=plannerID)


# Called when a user is trying to create a new planner
# Request must have params of title and username
@app.route('/new_planner', methods=['POST'])
def new_planner():
    if request.is_json:
        title = request.json['title']
        username = request.json['username']
    else:
        title = request.form['title']
        username = request.form['username']
    return database_login_utilities.db_create_planner(db=db, title=title, username=username)


# database models
class login_table(db.Model):
    __tablename__ = 'login_table'
    username = Column(String, primary_key=True, unique=True)
    password = Column(String)
    preferred_name = Column(String)
    related_tables = Column(String)
    related_events = Column(String)
    table_names = Column(String)


class Planner(db.Model):
    __tablename__ = 'Planner'
    unique_id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    title = Column(String)
    related_events = Column(String)
    creator_name = Column(String)
    password = Column(String)
    members_allowed = Column(String)


class Events(db.Model):
    __tablename__ = 'Events'
    unique_id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    date = Column(Integer)
    description = Column(String)
    creator_name = Column(String)
    parent_planner = Column(Integer)


# serializing methods, used by queries in database_login_utilites.py
class UserSchema(marsh.Schema):
    class Meta:
        fields = ('unique_id', 'username', 'password', 'preferred_name', 'related_tables', 'related_events', 'table_names')


class PlannerSchema(marsh.Schema):
    class Meta:
        fields = ('unique_id', 'title', 'related_events', 'creator_name', 'password', 'members_allowed')


class EventsSchema(marsh.Schema):
    class Meta:
        fields = ('unique_id', 'date', 'description', 'creator_name', 'parent_planner')


# defining the ability to de-serialize single and many objects
user_schema = UserSchema()
users_schema = UserSchema(many=True)

planner_schema = PlannerSchema()
planners_schema = PlannerSchema(many=True)


event_schema = EventsSchema()
events_schema = EventsSchema(many=True)


if __name__ == '__main__':
    db.create_all()
    if 'liveconsole' not in gethostname():
        app.run()
