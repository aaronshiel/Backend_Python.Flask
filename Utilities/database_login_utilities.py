from flask import jsonify
import hashlib
import flask_app


# Returns user data in JSON format
# Called when a user is creating a new account
def db_create_user(db, username: str, password: str):
    # check if username already exists in database
    user = flask_app.login_table.query.get(username)
    if user is not None:
        # username already exists in database
        return jsonify(message="That username is taken."), 401
    else:
        # username does not exist, create a new account
        new_user = flask_app.login_table(username="" + username + "",
                                         password="" + hash_password(password) + "",
                                         preferred_name=username,
                                         related_tables="",
                                         related_events="",
                                         table_names="")
        db.session.add(new_user)
        db.session.commit()
        # serialize user data to return in JSON
        result = flask_app.user_schema.dump(new_user)
        return jsonify(result), 201


# Queries login_table for user account info
# Returns user data in JSON format
# Called when a user is trying to log in
def db_login_user(db, username: str, password: str):
    user = db.session.query(flask_app.login_table)\
        .filter(flask_app.login_table.username == username).first()
    if user is None:
        return jsonify(message="account not found"), 404
    if hash_password(password) == user.password:
        result = flask_app.user_schema.dump(user)
        return jsonify(result), 200
    else:
        return jsonify(message="passwords do not match"), 412


# Updates Events database table with passed in event info
# Updates parent user and parent planner with new event
# Called when a user is trying to create a new event
def db_create_event(db, date, description, username, plannerID):
    # Adding new event to Event database
    new_event = flask_app.Events(date=date,
                                 description=description,
                                 creator_name=username,
                                 parent_planner=plannerID)
    db.session.add(new_event)
    db.session.flush()
    # grab user and update list of events in login_table table
    user = db.session.query(flask_app.login_table)\
        .filter(flask_app.login_table.username == username).first()
    # correctly append to ensure "," delimiter works correctly
    if user.related_tables == "":
        user.related_events = str(new_event.unique_id)
    else:
        user.related_events = user.related_events\
            + "," + str(new_event.unique_id)
    # grab parent planner and update list of events in Planners table
    planner = db.session.query(flask_app.Planner)\
    .filter(flask_app.Planner.unique_id == plannerID).first()
    # correctly append to ensure "," delimiter works correctly
    if planner.related_events == "":
        planner.related_events = str(new_event.unique_id)
    else:
        planner.related_events = planner.related_events\
            + "," + str(new_event.unique_id)
    db.session.commit()

    # return the event info for displaying on webpage
    result = flask_app.event_schema.dump(new_event)
    return jsonify(result), 200


# Updates Planners table with new planner
# Updates users list of planners with new planner
# Called when a user is trying to create a new planner
def db_create_planner(db, title, username):
    # Creating new planner
    new_planner = flask_app.Planner(title=title,
                                    creator_name=username,
                                    members_allowed=username,
                                    related_events="")
    db.session.add(new_planner)
    db.session.flush()
    # Grab user and update related planners and related planner titles
    user = db.session.query(flask_app.login_table)\
        .filter(flask_app.login_table.username == username).first()
    # correctly append to ensure "," delimiter works correctly
    if user.related_tables == "":
        user.related_tables = str(new_planner.unique_id)
    else:
        user.related_tables = user.related_tables\
        + "," + str(new_planner.unique_id)
    if user.table_names == "":
        user.table_names = title
    else:
        user.table_names = user.table_names + "," + title
    db.session.commit()
    return jsonify(message="planner created"), 200


# Queries and returns information of requested planner
# Called when user is trying to access an already created planner
def get_planner_info(db, planner_id):
    planner_info = db.session.query(flask_app.Planner)\
        .filter(flask_app.Planner.unique_id == planner_id).first()
    if planner_info is not None:
        new_planner = flask_app.Planner(unique_id=planner_info.unique_id,
                                        title=planner_info.title,
                                        related_events=planner_info.related_events,
                                        creator_name=planner_info.creator_name,
                                        password=planner_info.password,
                                        members_allowed=planner_info.members_allowed)
        results = flask_app.planner_schema.dump(new_planner)
        return jsonify(results), 200
    else:
        return jsonify(message="Planner of that ID does not exist"), 404


# Queries and returns info of a single event
# Called when a planner is opened
def get_event_info(db, event_id):
    event_info = db.session.query(flask_app.Events)\
        .filter(flask_app.Events.unique_id == event_id).first()
    if event_info is not None:
        new_event = flask_app.Events(unique_id=event_info.unique_id,
                                     date=event_info.date,
                                     description=event_info.description,
                                     creator_name=event_info.creator_name,
                                     parent_planner=event_info.parent_planner, )
        results = flask_app.event_schema.dump(new_event)
        return jsonify(results), 200
    else:
        return jsonify(message="Event of that ID does not exist"), 404


# Returns a hashed representation of password argument
def hash_password(password):
    hashpass = str.encode(password)
    hashpass = hashlib.md5(hashpass).hexdigest()
    return hashpass
