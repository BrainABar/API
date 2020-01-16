from flask import render_template, url_for, flash, redirect, request
from flask_restful import Resource
# from marshmallow import Schema, fields, pprint
from smshandler import app, db, config
from smshandler.models import Phone
from smshandler.twiliohandler import TwilioHandler

'''
MessagingSid/SmsSid = A 34 character unique identifier for the message. May be used to later retrieve this message from the REST API
AccountSid = The 34 character id of the Account this message is associated with.
MessagingServiceSid = The 34 character id of the Messaging Service associated with the message.
From = The phone number or Channel address that sent this message.
To = The phone number or Channel address of the recipient.
Body = The text body of the message. Up to 1600 characters long.
NumMedia = The number of media items associated with your message
NumSegments = Message broken into billable segments. Up to 1600, each segment should be around 140 characters.

Based on the twilio info based on To/From field(can be manipulated)
FromCity = The city of the sender
FromState = The state or province of the sender.
FromZip = The postal code of the called sender.
FromCountry = The country of the called sender.
ToCity = The city of the recipient.
ToState = The state or province of the recipient.
ToZip = The postal code of the recipient.
ToCountry = The country of the recipient.
'''

handler = TwilioHandler(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN, config.TWILIO_NUMBER)


@app.route("/incoming/", methods=['POST', 'GET'])
def incoming():
    if request.method == 'GET':
        return '', 404

    if request.method == 'POST':
        # authenticate
        url = request.url
        signature = request.headers.get('X-Twilio-Signature')
        parameters = request.form.to_dict()
        numberSize = 10
        response = None
        device_id = None

        if handler.authenticatesender(url, parameters, signature):
            # only accept requests from registered numbers
            body = request.form['Body']
            messagesid = request.form['MessageSid']
            nummedia = request.form['NumMedia']
            from_ = request.form['From']

            # phone numbers are saved without area code, US numbers only
            if len(from_) > numberSize:
                from_ = from_[len(from_)-numberSize:len(from_)]

            # device = db.session.query(Phone).filter(Phone.phone == from_)
            device = Phone.query.filter_by(phone=from_).first()
            body = body.lower()

            if device is not None:
                device_id = device.id

            # put messages in users
            # create new user to database
            if device is None:
                device = Phone(from_)
                db.session.add(device)
                response = "Reply with begin to start using with 10 free credits"
                db.session.commit()

            # user exists or added to database
            elif "begin" in body:
                if not device.freecredits:
                    response = "10 credits applied," \
                               "\nSms send under char limit are free," \
                               "\nGo to sms section of bryanbar website for more"
                    device.credits += 10
                    device.freecredits = True
                    device.sent += 1
                    device.received += nummedia
                    db.session.commit()

                else:
                    response = "Please navigate to sms section of bryanbar website to get more credits or for help" \
                               "\nContinuous spam will result in blacklist"
                    device.sent += 1
                    device.received += nummedia
                    db.session.commit()

            elif not device.freecredits:
                response = "Reply with begin to get 10 free credits or visit bryanbar for more help"
                device.sent += 1
                device.received += nummedia
                db.session.commit()

            elif device.credits > 0:
                if "test" in body:
                    response = "test body reply"
                    device.credits -= 1
                    device.sent += 1
                    device.received += nummedia
                    db.session.commit()

                elif "credits" in body:
                    response = "Credits under number: " + str(device.credits)
                    device.sent += 1
                    device.received += nummedia
                    db.session.commit()

                else:
                    response = "Unrecognized command, reply with 'help' or visit bryanbar website and visit sms"
                    device.sent += 1
                    device.received += nummedia
                    db.session.commit()

            else:
                response = "Please head over to bryanbar website to add more credits or for help"
                device.sent += 1
                device.received += nummedia
                db.session.commit()

            handler.createmessage(response, device.phone)

            return '', 202

        return '', 404


@app.route("/")
def index():
    return "Index", 200
