from pymodm import connect, MongoModel, fields
import models
from pymodm.errors import DoesNotExist
from flask import Flask, jsonify, request
import numpy as np
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
connect("mongodb://localhost:27017/bme590")  # connect to database


@app.route('/api/heart_rate', methods=['POST'])
def add_data():

    """ Adds data to the database. If the user does not exist, creates a new user.
        :returns x: True if user exists or False if user does not exist """

    r = request.get_json()
    email = r["user_email"]
    age = r["user_age"]
    heart_rate = r["heart_rate"]
    try:
        add_heart_rate(email, heart_rate, datetime.datetime.now())  # add data to existing user
        x = jsonify({'user email': email, 'heart_rate': heart_rate, 'time': datetime.datetime.now()})
    except DoesNotExist:
        create_user(email, age, heart_rate, datetime.datetime.now())  # if user does not exist, create new user
        x = jsonify({'user email': email, 'user_age': age, 'heart_rate': heart_rate, 'time': datetime.datetime.now()})
    return x


@app.route('/api/heart_rate/<user_email>', methods=['GET'])
def get_data(user_email):

    """ Gets heart rate data in the form of a json string
        :param user_email: email address of user corresponding to heart rate
        :returns heart_data: A json string of the user's heart rates """

    try:
        user = models.User.objects.raw({'_id': user_email}).first()
        heart_data = user.heart_rate
        print("This user does not exist")
        return jsonify({'heart_rate': heart_data}), 200
    except DoesNotExist:
        return 400


@app.route('/api/heart_rate/average/<user_email>', methods=['GET'])
def get_average(user_email):

    """ Gets average heart rate of user (average of all inputs)
        :param: user_email: email address of user corresponding to heart rate
        :returns average: A json string of the user's average heart rate """

    try:
        user = models.User.objects.raw({'_id': user_email}).first()
        heart_data = user.heart_rate
        average = average_calc(heart_data)
        return jsonify({'average_heart_rate': average})
    except DoesNotExist:
        return 400


@app.route('/api/heart_rate/interval_average', methods=['POST'])
def get_interval_average():

    """ Gets average heart rate of user (average of all inputs)
        :param: user_email: email address of user corresponding to heart rate
        :param: interval_start: date and time after which heart rate average should be taken
        :returns interval_average: A json string of the user's average heart rate """

    r = request.get_json()

    email = r["user_email"]
    interval_start = r["heart_rate_average_since"]
    age = r["user_age"]

    try:
        user = models.User.objects.raw({"_id": email}).first()
        heart_data = user.heart_rate
        heart_time = user.heart_rate_times
        interval_average = interval_average_calc(heart_time, heart_data, interval_start)
        return jsonify({'heart_rate_average_since': interval_average, 'tachycardia': tachy_check(interval_average, age)})
    except DoesNotExist:
        return 400


def add_heart_rate(email, heart_rate, time):

    """ Adds a heart rate to an existing user
    :param: email: email address of user corresponding to heart rate
    :param: heart_rate: heart rate of the user
    :param: time: time at which heart rate of the user was entered """

    user = models.User.objects.raw({"_id": email}).first()  # Get the first user where _id=email
    user.heart_rate.append(heart_rate)  # Append the heart_rate to the user's list of heart rates
    user.heart_rate_times.append(time)  # append the current time to the user's list of heart rate times
    user.save()  # save the user to the database


def create_user(email, age, heart_rate, time):

    """ Creates a new user with email, age, heart rate, and data entry time
    :param: email: email address of user corresponding to heart rate
    :param: age: age of the user
    :param: heart_rate: heart rate of the user
    :param: time: time at which heart rate of the user was entered """

    u = models.User(email, age, [], [])  # create a new User instance
    u.heart_rate.append(heart_rate)  # add initial heart rate
    u.heart_rate_times.append(time)  # add initial heart rate time
    u.save()  # save the user to the database


def print_user(email):

    """ Prints user data (email, heart rate, and data entry time)
        :param: email: email address of user corresponding to heart rate """

    user = models.User.objects.raw({"_id": email}).first()  # Get the first user where _id=email
    print(user.email)
    print(user.heart_rate)
    print(user.heart_rate_times)


def average_calc(heart_data):

    """ Calculates average heart rate of user.
        :param: heart_data: heart rate data
        :returns np.mean(heart_data): average heart rate"""

    return np.mean(heart_data)


def interval_average_calc(h_time, h_data, interval_start):

    """ Gets average heart rate of user after a specified time.
        :param: h_time: times at which heart rate data was recorded
        :param: h_data: heart rate data
        :param: interval_start: date and time after which heart rate average should be taken
        :returns np.mean(interval): Average heart rate after specified start time"""

    start = datetime.datetime.strptime(interval_start, "%Y-%m-%d %H:%M:%S.%f")
    interval = []
    for i, time in enumerate(h_time):
        if time > start:
            interval.append(h_data[i])
    return np.mean(interval)


def tachy_check(heart_rate, age):
    """ Returns true if user has tachycardia and false if the user does not have tachycardia
        :param heart_rate: Heart rate of the user
        :param age: Age of the user """

    age = int(age)
    heart_rate = int(heart_rate)

    if age <= 1 and heart_rate >= 159:
        return True
    elif age <= 2 and heart_rate >= 151:
        return True
    elif age <= 4 and heart_rate >= 137:
        return True
    elif age <= 7 and heart_rate >= 133:
        return True
    elif age <= 11 and heart_rate >= 130:
        return True
    elif age <= 15 and heart_rate >= 119:
        return True
    elif heart_rate >= 100:
        return True

    else:
        return False


if __name__ == "__main__":
    app.run(host="127.0.0.1")
