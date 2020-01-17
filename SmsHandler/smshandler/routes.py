from flask import render_template, url_for, flash, redirect, request
from flask_restful import Resource
# from marshmallow import Schema, fields, pprint
from smshandler import app, db, config
from smshandler.models import Phone, Messagesid
from smshandler.twiliohandler import TwilioHandler
import requests
import herepy

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
            messagesid = request.form['MessageSid']  # twilio automatically saves messages, retrieve with messagesid
            nummedia = int(request.form['NumMedia'])
            from_ = request.form['From']

            # phone numbers are saved without area code, US numbers only
            if len(from_) > numberSize:
                from_ = from_[len(from_)-numberSize:len(from_)]

            # device = db.session.query(Phone).filter(Phone.phone == from_) Do similar
            device = Phone.query.filter_by(phone=from_).first()
            body = body.lower()
            body = body.split(":")

            if device is not None:
                device_id = device.id

            # put messages in users
            # create new user to database
            if device is None:
                device = Phone(from_)
                db.session.add(device)
                response = "Reply with begin to start using with 10 free credits"

            # user exists or added to database
            elif "begin" in body[0]:
                if not device.free_credits or device.unlimited:
                    response = "10 credits applied," \
                               "\nSms send under char limit are free," \
                               "\nGo to sms section of bryanbar website for more"
                    device.credits += 10
                    device.free_credits = True

                else:
                    response = "Please navigate to sms section of bryanbar website to get more credits or for help" \
                               "\nContinuous spam will result in blacklist"

            elif not device.free_credits:
                response = "Reply with begin to get 10 free credits or visit bryanbar for more help"

            elif device.credits > 0:
                if "quote" in body[0]:
                    response = "random quote here"
                    device.credits -= 1

                elif "credits" in body[0]:
                    response = "Credits under number: " + str(device.credits)

                elif "nearby" in body[0]:
                    xypos = None  # will be a dictionary of Latitude and Longitude keys
                    search = ""  # string of users command
                    response = ""
                    geo_api = herepy.GeocoderApi(config.HERE_API_KEY)
                    loc = None

                    if len(body) >= 2:

                        if len(body[1].split(" ")) == 1:  # single address assumed to be zip code, needs US to refine
                            if body[1].isdigit():
                                loc = geo_api.free_form(body[1] + " US")
                        else:
                            loc = geo_api.free_form(body[1])

                        if len(loc.Response['View']) >= 1:

                            xypos = loc.Response['View'][0]['Result'][0]["Location"]["DisplayPosition"]

                            if len(body) >= 3:
                                search = body[2]

                                if len(body) >= 4:
                                    for text in body[3:]:
                                        search += " " + text
                            else:
                                search = "food"

                            place_api = herepy.PlacesApi(config.HERE_API_KEY)
                            coor = [xypos['Latitude'], xypos['Longitude']]
                            locresults = place_api.onebox_search(coor, search)

                            if locresults.results['items']:
                                for item in locresults.results['items']:
                                    tempstr = item['title']

                                    if len(response) + len(tempstr) <= 140:
                                        response += tempstr + '\n'
                                    else:
                                        break

                            else:
                                response = "No search results"

                            device.credits -= 1

                        else:
                            response = "Check location, results returned nothing\n" \
                                       "nearby {location} {search words}"
                    else:
                        response = "Location should be all digits\n" \
                                   "nearby {location} {search words}"

                else:
                    response = "Unrecognized command, reply with 'help' or visit bryanbar website and visit sms"

            else:
                response = "Please head over to bryanbar website to add more credits or for help"

            handler.createmessage(response, device.phone)
            device.sent += 1
            device.received += nummedia
            msg_sid = Messagesid()
            msg_sid.sid_tag = messagesid
            device.message_sids.append(msg_sid)
            db.session.commit()

            return '', 202

        return '', 404


@app.route("/")
def index():
    return "Index", 200
