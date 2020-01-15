from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from smshandler import config as configfile
from smshandler import twiliohandler

# Init
app = Flask(__name__)
config = configfile.Config

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Twilio Handler
handler = twiliohandler.TwilioHandler(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN, config.TWILIO_NUMBER)

from smshandler import routes