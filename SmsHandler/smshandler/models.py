import datetime
from smshandler import db


class Phone(db.Model):
    __tablename__ = "phones"

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String, unique=True, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    freecredits = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)
    messages = db.relationship('Messages', backref='number', lazy=True)
    stats = db.relationship('Statistics', backref='owner', lazy=True)

    def __init__(self, phone):
        self.phone = phone

    def __repr__(self):
        return '<Phone> %r' % self.phone


class Messages(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(140))
    reply = db.Column(db.String(140))
    date = db.Column(db.DateTime)
    number_id = db.Column(db.Integer, db.ForeignKey('phones.id'), nullable=False)

    def __init__(self):
        self.date = datetime.datetime.now()

    def __repr__(self):
        return '<Message> %r' % self.message


class Statistics(db.Model):
    __tablename__ = "statistics"

    id = db.Column(db.Integer, primary_key=True)
    sent = db.Column(db.Integer, default=0)
    received = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('phones.id'), nullable=False)

    def __repr__(self):
        return '<Received> %r' % self.received

    def __init__(self):
        self.sent = 0
        self.received = 0
