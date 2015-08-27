from rest_framework.exceptions import APIException

__author__ = 'sacherus'


class WinkException(APIException):
    status_code = 400
    default_detail = 'Wink Api Exception'

    def __init__(self, msg):
        self.detail = {"errors": [msg]}
