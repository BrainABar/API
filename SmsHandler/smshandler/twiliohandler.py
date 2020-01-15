from twilio.rest import Client
from twilio.request_validator import RequestValidator
from smshandler.models import Phone, Message, Statistics
from smshandler import db


class TwilioHandler:

    def __init__(self, account_sid,
                 auth_token, from_):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_ = from_
        self.client = Client(account_sid, auth_token)

    def authenticatesender(self, url, parameters, signature):

        if signature and url and parameters:

            validator = RequestValidator(self.auth_token)

            if validator.validate(url, parameters, signature):
                return True

        return False

    def processcontent(self, body, messagesid, nummedia, from_):

        response = None

        #device = db.session.query(Phone).filter(Phone.phone == from_)
        device = Phone.query.filter_by(phone=from_).first()
        body = body.lower()

        # put messages in users
        # create new user to database
        if device is None:
            device = Phone(from_)
            device.stats.append(Statistics())

            response = "Hello, welcome to Sms helper. Reply with 'begin' to get one time" \
                       "10 credits added under sending number or 'help' for more info"

            device.messages.append(Message(body, response))
            self.createmessage(response, device.phone)
            device.stats[0].received += nummedia
            device.stats[0].sent += 1
            db.session.add(device)
            db.session.commit()

        # user exists in database
        else:
            device = device.first()

            if "begin" in body:
                if not device.freecredits:
                    response = "10 credits applied," \
                           "\nSms send under char limit are free," \
                           "\nGo to sms section of bryanbar website for more"
                    device.stats[0].credits += 10
                    device.freecredits = True
                else:
                    response = "Please navigate to sms section of bryanbar website to get more credits or for help," \
                                "Continuous spam will result in blacklist"

            elif device.stats[0].credits > 0:
                if "test" in body:
                    response = "test body reply"
                    device.stats[0].credits -= 1

                elif "credits" in body:
                    response = "Credits under number: " + str(device.stats[0].credits)

                else:
                    response = "Unrecognized command, reply with 'help' or visit bryanbar website and visit sms"

            elif device.stats[0].credits <= 0:
                response = "Please head over to bryanbar website to add more credits"

            device.messages.append(Message(body, response))
            self.createmessage(response, device.phone)
            device.stats[0].sent += 1
            device.stats[0].received += nummedia
            db.session.commit()

        return '', 202

    def createmessage(self, body, to):
        message = self.client.messages.create(body=body, from_=self.from_, to=to)
        return message