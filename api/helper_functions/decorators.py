import os
import jwt
from functools import wraps
from flask import make_response, jsonify, request


def requires_authentication(func):
    """Decorates endpoints for which authentication is required
    """
    @wraps(func)
    def auth_wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            response = {
                "message": "Authorization headers are missing"
            }

            return make_response(jsonify(response)), 401
        auth_token = request.headers['Authorization']
        secret_key = os.getenv('SECRET_KEY')
        try:
            user_id = jwt.decode(auth_token, secret_key)['sub']
            return func(user_id, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            response = {
                "message": "Token expired, log in to obtain another token"
            }

            return make_response(jsonify(response)), 401

        except jwt.InvalidTokenError:
            response = {
                "message": "Invalid token, log in to obtain token"
            }

            return make_response(jsonify(response)), 401

    return auth_wrapper
