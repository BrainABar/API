from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from smshandler import config as configfile

#Init
app = Flask(__name__)
config = configfile.Config

#Database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

from smshandler import routes