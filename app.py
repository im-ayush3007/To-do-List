from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from logging_config import setup_logging

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

setup_logging(app)

from routes import *