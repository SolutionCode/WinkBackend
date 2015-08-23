from json import dumps, loads
import base64
from functools import wraps

from django.test import TestCase
from django.test.client import Client
from oauth2_provider.models import Application
from users.models import User


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
    token = None

    @process_response
    def post(self, path, data=None, **kwargs):
        if isinstance(data, dict):
            data = dumps(data)
            kwargs['content_type'] = 'application/json'

        if self.token:
            kwargs['HTTP_AUTHORIZATION'] = 'Bearer ' + self.token

        return super(APITestClient, self).post(path, data, **kwargs)

    @process_response
    def get(self, *args, **kwargs):
        if self.token:
            kwargs['HTTP_AUTHORIZATION'] = 'Bearer ' + self.token

        return super(APITestClient, self).get(*args, **kwargs)

    def set_token(self, token):
        self.token = token


class APITestsBase(TestCase):
    STATUS_CODE_OK = 200
    STATUS_CODE_CREATED = 201
    STATUS_CODE_BAD_REQUEST = 400
    STATUS_CODE_UNAUTHORIZED = 401
    STATUS_CODE_PERMISSION_DENIED = 403
    STATUS_CODE_NOT_FOUND = 404
    STATUS_CODE_VALIDATION_ERROR = 422
    client_class = APITestClient

    def assertAPIReturnedValidationErrorStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_VALIDATION_ERROR)

    def assertAPIValidationErrorHasKey(self, response, key):
        data = loads(response.content)
        error_key = 'errors' if 'errors' in data else 'error'
        self.assertTrue(key in data[error_key])

    def assertAPIReturnedKey(self, response, key, value=None):
        if value:
            self.assertTrue(response.data.get(key) == value,
                            "key: %s, doesn't have val: %s, instead: %s" % (key, value, response.data.get(key)))
        else:
            self.assertIsNotNone(response.data.get(key))

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


class APITestClientLogin(APITestsBase):
    APP_USER_DATA = {
        'email': 'app@app.com',
        'display_name': 'Test App',
        'username': '@app_username',
        'password': 'app_password'
    }

    VALID_USER_DATA = {
        'email': 'test@example.com',
        'display_name': 'Test User',
        'username': '@username',
        'password': 'password'
    }

    OAUTH2_URL = '/oauth2/token/'

    def setUp(self):
        self.app_user, self.app = self.__get_application()

    def __get_application(self):
        user = User.objects.create_user(**self.APP_USER_DATA)
        app = Application.objects.create(user=user,
                                         client_type=Application.CLIENT_CONFIDENTIAL,
                                         authorization_grant_type=Application.GRANT_PASSWORD)
        return user, app

    def __get_auth_header(self, app):
        return self.__get_auth_headers_raw(app.client_id, app.client_secret)

    def __get_auth_headers_raw(self, id, secret):
        return {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(id + ':' + secret),
        }

    def __user_data2auth_data(self, user_data):
        return {'grant_type': 'password', 'username': user_data['email'], 'password': user_data['password']}

    def get_valid_user(self):
        return User.objects.create_user(**self.VALID_USER_DATA)

    def login(self, user_data):
        data = self.__user_data2auth_data(user_data)
        return self.client.post(self.OAUTH2_URL, data=data, **self.__get_auth_header(self.app))

    def login_persistent(self, user_data):
        response = self.login(user_data)
        self.client.set_token(response.data['access_token'])
