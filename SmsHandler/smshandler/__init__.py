from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from smshandler import config as configfile

#Init
db = SQLAlchemy()
app = Flask(__name__)
db.init_app(app)
config = configfile.Config

#Database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI


from smshandler import routes