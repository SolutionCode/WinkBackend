from rest_framework.exceptions import APIException

__author__ = 'sacherus'


class WinkException(APIException):
    default_detail = 'Wink api general exception'

    def __init__(self, msg):
        self.detail = {"errors": msg}


class WinkParseException(WinkException):
    status_code = 400
    default_detail = 'Wink parse exception'

    def __init__(self, msg):
        super(WinkParseException, self).__init__([msg])
