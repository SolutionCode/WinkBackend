from json import dumps, loads
from functools import wraps

from django.test import TestCase
from django.test.client import Client


def process_response(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        response = func(*args, **kwargs)
        if 'Content-Type' in response and response['Content-Type'] == 'application/json':
            setattr(response, 'data', loads(response.content))
        else:
            setattr(response, 'data', response.content)
        return response

    return decorated


class APITestClient(Client):

    @process_response
    def post(self, path, data=None, **kwargs):
        if isinstance(data, dict):
            data = dumps(data)
            kwargs['content_type'] = 'application/json'

        return super(APITestClient, self).post(path, data, **kwargs)

    @process_response
    def get(self, *args, **kwargs):
        return super(APITestClient, self).get(*args, **kwargs)


class APITestsBase(TestCase):
    STATUS_CODE_OK = 200
    STATUS_CODE_CREATED = 201
    STATUS_CODE_UNAUTHORIZED = 401
    STATUS_CODE_PERMISSION_DENIED = 403
    STATUS_CODE_NOT_FOUND = 404
    STATUS_CODE_VALIDATION_ERROR = 422
    client_class = APITestClient

    def assertAPIReturnedValidationErrorStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_VALIDATION_ERROR)

    def assertAPIValidationErrorHasKey(self, response, key):
        data = loads(response.content)
        self.assertTrue(key in data['errors'])

    def assertAPIReturnedCreatedStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_CREATED)

    def assertAPIReturnedOKStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_OK)

    def assertAPIReturnedNotFoundStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_NOT_FOUND)

    def assertAPIReturnedUnauthorized(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_UNAUTHORIZED)

    def assertAPIReturnedPermissionDenied(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_PERMISSION_DENIED)