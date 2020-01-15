import json

with open('/etc/config.json') as config_file:
    config = json.load(config_file)


class Config:

    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    TWILIO_ACCOUNT_SID = config.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = config.get('TWILIO_AUTH_TOKEN')
    TWILIO_NUMBER = config.get('TWILIO_NUMBER')
