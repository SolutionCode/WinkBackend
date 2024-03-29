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
    auth_header = None

    def _patch_data(self, kwargs):
        data = kwargs.get('data')
        if isinstance(data, dict):
            data = dumps(data)
            kwargs['data'] = data
            kwargs['content_type'] = 'application/json'

    def _add_token(self, kwargs):
        if self.token:
            kwargs['HTTP_AUTHORIZATION'] = 'Bearer ' + self.token

    def _add_auth_header(self, kwargs):
        kwargs['HTTP_AUTHORIZATION'] = 'Basic ' + self.auth_header

    @process_response
    def post(self, *args, **kwargs):
        self._patch_data(kwargs)
        self._add_token(kwargs)

        return super(APITestClient, self).post(*args, **kwargs)

    @process_response
    def post_with_auth_header(self, *args, **kwargs):
        """
        calling post from ApiTest will overide token header! 40 minutes for debuging
        """
        self._patch_data(kwargs)
        self._add_auth_header(kwargs)

        return super(APITestClient, self).post(*args, **kwargs)

    @process_response
    def get(self, *args, **kwargs):
        self._add_token(kwargs)

        return super(APITestClient, self).get(*args, **kwargs)

    @process_response
    def patch(self, *args, **kwargs):
        self._patch_data(kwargs)
        self._add_token(kwargs)

        return super(APITestClient, self).patch(*args, **kwargs)

    @process_response
    def put(self, *args, **kwargs):
        self._patch_data(kwargs)
        self._add_token(kwargs)

        return super(APITestClient, self).put(*args, **kwargs)

    def set_token(self, token):
        self.token = token

    def set_auth_header(self, auth_header):
        self.auth_header = auth_header


class APITestsBase(TestCase):
    STATUS_CODE_OK = 200
    STATUS_CODE_CREATED = 201
    STATUS_CODE_BAD_REQUEST = 400
    STATUS_CODE_UNAUTHORIZED = 401
    STATUS_CODE_FORBIDDEN = 403
    STATUS_CODE_NOT_FOUND = 404
    STATUS_CODE_METHOD_NOT_ALLOWED = 405
    STATUS_CODE_VALIDATION_ERROR = 422
    client_class = APITestClient

    PASSWORD = 'password123'
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
        'password': PASSWORD
    }

    # TODO: Can I access those urls from settins or some reversed search?
    # LD: yes, just use reverse() in setUp
    OAUTH2_URL = '/tokens/oauth2/'
    OAUTH2_TOKEN_URL = OAUTH2_URL + 'token/'
    OAUTH2_REVOKE_URL = OAUTH2_URL + 'revoke_token/'

    def setUp(self):
        self.app_user, self.app = self.__get_application()
        self.client.set_auth_header(self._get_auth_header_value(self.app))

    def __get_application(self):
        user = User.objects.create_user(**self.APP_USER_DATA)
        app = Application.objects.create(user=user,
                                         client_type=Application.CLIENT_CONFIDENTIAL,
                                         authorization_grant_type=Application.GRANT_PASSWORD,
                                         name='wink-android')
        return user, app

    def _get_auth_header_value(self, app):
        return base64.b64encode(app.client_id + ':' + app.client_secret)

    def _user_data2auth_data(self, user):
        return {'grant_type': 'password', 'username': user.email, 'password': self.PASSWORD}

    def create_user(self, **kwargs):
        user_data = self.VALID_USER_DATA
        user_data.update(**kwargs)
        return User.objects.create_user(**user_data)

    def login(self, user):
        data = self._user_data2auth_data(user)
        return self.client.post_with_auth_header(self.OAUTH2_TOKEN_URL, data=data)

    def logout(self):
        return self.client.post_with_auth_header(self.OAUTH2_REVOKE_URL, data={'token': self.client.token})

    def login_persistent(self, user):
        response = self.login(user)
        self.client.set_token(response.data['access_token'])

    def check_valid_token(self, data):
        data = data['data']['token']
        self.assertAPIReturnedKey(data, 'token_type', 'Bearer')
        self.assertIsNotNone(data['access_token'])
        self.assertIsNotNone(data['refresh_token'])
        self.assertIsNotNone(data['expires_in'])
        self.assertIsNotNone(data['scope'])

    def assertAPIReturnedValidationErrorStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_VALIDATION_ERROR)

    def assertAPIValidationErrorHasKey(self, response, key):
        data = loads(response.content)
        self.assertTrue(key in data['errors'])

    def assertAPIReturnedKey(self, data, key, value=None):
        if value:
            self.assertTrue(data.get(key) == value,
                            "key: %s, doesn't have val: %s, instead: %s" % (key, value, data.get(key)))
        else:
            self.assertIsNotNone(data.get(key))

    def assertAPIReturnedCreatedStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_CREATED)

    def assertAPIReturnedOKStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_OK)

    def assertAPIReturnedNotFoundStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_NOT_FOUND)

    def assertAPIReturnedUnauthorized(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_UNAUTHORIZED)

    def assertAPIReturnedForbiddenStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_FORBIDDEN)

    def assertAPIReturnedMethodNotAllowedStatus(self, response):
        self.assertEquals(response.status_code, self.STATUS_CODE_METHOD_NOT_ALLOWED)
