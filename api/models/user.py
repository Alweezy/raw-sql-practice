import os
import jwt
from datetime import datetime, timedelta
from passlib.apps import custom_app_context as password_hash
from database.config import open_connection
from flask import jsonify, make_response


class User(object):

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def user_exists(self):
        """Check for user presence in the database
        """
        conn = open_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email='{}'".format(self.email))
        user = cur.fetchone()
        cur.close()
        return user

    def user_details(self):
        """Fetch user data from the database
        """
        user = self.user_exists()

        if user:
            user_data = dict

            user_data['user_id'] = user[0]
            user_data['username'] = user[1]

            return user_data

        else:
            response = {
                "message": "The user does not exist"
            }

            return make_response(jsonify(response)), 401

    def register_user(self, username):
        """
        Sign up a user
        """
        user_exists = self.user_exists()

        if user_exists:
            response = {
                "message": "Email already in use, try a different one"
            }

            return make_response(jsonify(response)), 409
        else:
            hashed_password = password_hash.encrypt(self.password)
            conn = open_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, email, password) VALUES('{}', '{}', '{}')"
                         .format(username, self.email, hashed_password))

            cur.close()
            conn.commit()

            response = {
                "message": "User registration successful!"
            }

            return make_response(jsonify(response)), 201

    def user_login(self):
        """sign in a registered user
        """
        user_exists = self.user_exists()
        password_match = self.verify_password(user_exists[3])

        if user_exists and password_match:
            token = self.generate_token(user_exists[0])
            response = {
                "message": "Login successful!",
                "token": token.decode('utf-8')
            }

            return make_response(jsonify(response)), 200

        else:
            response = {
                "message": "The user does not exist, register user first"
            }

            return make_response(jsonify(response)), 401

    def verify_password(self, stored_password):
        """Compare entered password to stored password
        """
        return password_hash.verify(self.password, stored_password)

    def generate_token(self, user_id):
        """Generate token based on user_id
        """
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(hours=10),
                'iat': datetime.utcnow(),
                'sub': user_id
            }

            secret = os.getenv('SECRET_KEY')
            token = jwt.encode(
                payload,
                secret,
                algorithm='HS256'
            )

            return token

        except Exception as e:
            return str(e)



