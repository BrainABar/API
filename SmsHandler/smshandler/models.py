import datetime
from smshandler import db


class Phone(db.Model):
    __tablename__ = "phones"

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    free_credits = db.Column(db.Boolean, default=False)
    unlimited = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)
    credits = db.Column(db.Integer, default=0)
    sent = db.Column(db.Integer, default=0)
    received = db.Column(db.Integer, default=0)
    message_sids = db.relationship('Messagesid', backref='phone', lazy=True)

    def __init__(self, phone):
        self.phone = phone

    def __repr__(self):
        return '<PHONENUMBER> %r' % self.phone


class Messagesid(db.Model):
    __tablename__ = "messagesids"

    id = db.Column(db.Integer, primary_key=True)
    sid_tag = db.Column(db.String(40), default="None")
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    phone_id = db.Column(db.Integer, db.ForeignKey('phone.id'), nullable=False)

    def __init__(self):
        date = datetime.datetime.utcnow()

    def __repr__(self):
        return '<MESSAGESID> %r' % str(self.sid_tag)
