import datetime
from smshandler import db


class Phone(db.Model):
    __tablename__ = "phones"

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String, unique=True, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    freecredits = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)
    sent = db.Column(db.Integer, default=0)
    received = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=0)

    def __init__(self, phone):
        self.phone = phone

    def __repr__(self):
        return '<Phone> %r' % self.phone