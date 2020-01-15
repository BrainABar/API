from flask import render_template, url_for, flash, redirect, request
from flask_restful import Resource
# from marshmallow import Schema, fields, pprint
from smshandler import app, config
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


@app.route("/incoming/", methods=['POST', 'GET'])
def incoming():
    if request.method == 'GET':
        return '', 404

    if request.method == 'POST':
        # authenticate
        handler = TwilioHandler(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN, config.TWILIO_NUMBER)
        url = request.url
        signature = request.headers.get('X-Twilio-Signature')
        parameters = request.form.to_dict()
        numberSize = 10

        if handler.authenticatesender(url, parameters, signature):
            # only accept requests from registered numbers
            body = request.form['Body']
            messagesid = request.form['MessageSid']
            nummedia = request.form['NumMedia']
            from_ = request.form['From']

            # phone numbers are saved without area code, US numbers only
            if len(from_) > numberSize:
                from_ = from_[len(from_)-numberSize:len(from_)]

            # returns status of processed content for twilio server in a TwiML format
            body, code = handler.processcontent(body, messagesid, nummedia, from_)
            return body, code

        return '', 404


@app.route("/")
def index():
    return "Index", 200