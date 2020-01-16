from twilio.rest import Client
from twilio.request_validator import RequestValidator


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

    def createmessage(self, body, to):
        message = self.client.messages.create(body=body, from_=self.from_, to=to)
        return message
