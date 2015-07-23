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
    STATUS_CODE_VALIDATION_ERROR = 422
    client_class = APITestClient

    def assertAPIReturnedValidationError(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_VALIDATION_ERROR)

    def assertAPIValidationErrorHasKey(self, response, key):
        data = loads(response.content)
        self.assertTrue(key in data['errors'])

