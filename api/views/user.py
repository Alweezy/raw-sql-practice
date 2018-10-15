import re
from flask import jsonify, request, make_response

from . import api
from api.models.user import User
from database.config import open_connection, close_connection
from api import app

email_regex = r"(^[a-zA-z0-9_.]+@[a-zA-z0-9-]+\.[a-z]+$)"
special_characters = re.compile(r"[<>/{}[\]~`*!@#$%^&()=+0-9]")


@api.route("/auth/signup", methods=['POST'])
def signup():
    conn = open_connection()
    cur = conn.cursor()
    email = request.get_json('email')['email']
    password = request.get_json('password')['password']
    username = request.get_json('username')['username']

    cur.execute("SELECT * FROM users WHERE username = '{}'".format(username))
    user_names = cur.fetchall()

    if user_names:
        response = {
            "message": "username is already taken, choose a different one"
        }

        return make_response(jsonify(response)), 409

    if special_characters.search(username):
        response = {
            "message": "Username should not contain special characters"
        }

        return make_response(jsonify(response)), 400

    if not request.json:
        response = {
            "message": "Bad request format"
        }

        return make_response(jsonify(response)), 400

    user = User(email, password)
    register = user.register_user(username)
    cur.close()
    close_connection(conn)
    return register


@api.route("/auth/login", methods=["POST"])
def login():
    """Login a registered user
    """
    email = request.get_json('email')['email']
    password = request.get_json('password')['password']

    if not email and password:
        response = {
            "message": "Email or password cannot be blank"
        }

        return make_response(jsonify(response)), 400

    if not re.match(email_regex, email):
        response = {
            "message": "Invalid email format"
        }

        return make_response(jsonify(response)), 400

    else:
        user = User(email, password)
        user_login = user.user_login()
        return user_login


