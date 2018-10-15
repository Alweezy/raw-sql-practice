from flask import Flask
from flask_cors import CORS
from database import create_tables


create_tables.create_tables()
app = Flask(__name__)
CORS(app)


app.url_map.strict_slashes = False
from .views import api, user, question


app.register_blueprint(api, url_prefix='/api/v1')
