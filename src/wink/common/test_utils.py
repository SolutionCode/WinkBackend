from json import dumps
from django.test import TestCase
from django.test.client import Client


class APITestClient(Client):

    def post(self, path, data=None, **kwargs):
        if isinstance(data, dict):
            data = dumps(data)
            kwargs['content_type'] = 'application/json'

        return super(APITestClient, self).post(path, data, **kwargs)


class APITestsBase(TestCase):
    client_class = APITestClient


