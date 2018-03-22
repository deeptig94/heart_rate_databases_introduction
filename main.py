from pymodm import connect, MongoModel, fields
import models
import datetime
from pymodm.errors import DoesNotExist
from flask import Flask, jsonify, request

app = Flask(__name__)
connect("mongodb://localhost:27017/bme590")  # connect to database


@app.route('/heart_rate', methods=['POST'])
def add_data():
    r = request.get_json()
    email = r["user_email"]
    age = r["user_age"]
    heart_rate = r["heart_rate"]
    try:
        add_heart_rate(email, heart_rate, datetime.datetime.now())
        x = print("updated user information"), True
    except DoesNotExist:
        create_user(email, age, heart_rate)
        x = print("created new user"), False
    return x


@app.route('/heart_rate/<user_email>', methods=['GET'])
def get_data(user_email):
    user = models.User.objects.raw({'_id': user_email}).first()
    data_list = user.heart_rate
    return jsonify({'heart_rate': data_list})


def add_heart_rate(email, heart_rate, time):
    user = models.User.objects.raw({"_id": email}).first()  # Get the first user where _id=email
    user.heart_rate.append(heart_rate)  # Append the heart_rate to the user's list of heart rates
    user.heart_rate_times.append(time)  # append the current time to the user's list of heart rate times
    user.save()  # save the user to the database


def create_user(email, age, heart_rate):
    u = models.User(email, age, [], [])  # create a new User instance
    u.heart_rate.append(heart_rate)  # add initial heart rate
    u.heart_rate_times.append(datetime.datetime.now()) # add initial heart rate time
    u.save()  # save the user to the database


def print_user(email):
    user = models.User.objects.raw({"_id": email}).first()  # Get the first user where _id=email
    print(user.email)
    print(user.heart_rate)
    print(user.heart_rate_times)


if __name__ == "__main__":
    connect("mongodb://localhost:27017/heart_rate_app")  # open up connection to db
    create_user(email="suyash@suyashkumar.com", age=24, heart_rate=60)
    # we should only do this once, otherwise will overwrite existing user
    add_heart_rate("suyash@suyashkumar.com", 60, datetime.datetime.now())
    print_user("suyash@suyashkumar.com")
