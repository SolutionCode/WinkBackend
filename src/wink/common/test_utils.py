from json import dumps, loads
from django.test import TestCase
from django.test.client import Client


class APITestClient(Client):

    def post(self, path, data=None, **kwargs):
        if isinstance(data, dict):
            data = dumps(data)
            kwargs['content_type'] = 'application/json'

        return super(APITestClient, self).post(path, data, **kwargs)


class APITestsBase(TestCase):
    STATUS_CODE_OK = 200
    STATUS_CODE_CREATED = 201
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