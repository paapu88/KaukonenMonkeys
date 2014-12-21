from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import basedir
from flask.ext.heroku import Heroku

app = Flask(__name__)
#app.config.from_object('../config')
app.config.from_pyfile('../config.py')
heroku = Heroku(app)
db = SQLAlchemy(app)

from app import views, models

