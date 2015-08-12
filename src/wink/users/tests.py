import base64

from oauth2_provider.models import Application
from common.test_utils import APITestsBase
from users.models import User

class UserAPITestCase(APITestsBase):
    VALID_USER_DATA = {
        'email': 'test@example.com',
        'display_name': 'Test User',
        'username': '@username',
        'password': 'password'
    }

    def test_get_existing_user(self):
        user = User.objects.create(email=self.VALID_USER_DATA['email'])

        response = self.client.get('/users/{pk}'.format(pk=user.pk), follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data
        self.assertEquals(data['id'], user.pk)
        self.assertEquals(data['email'], user.email)

    def test_get_not_existing_user(self):
        response = self.client.get('/users/1', follow=True)
        self.assertAPIReturnedNotFoundStatus(response)

    def test_create_user(self):
        response = self.client.post('/users/', data=self.VALID_USER_DATA)
        self.assertEquals(User.objects.count(), 1)
        user = User.objects.first()

        self.assertAPIReturnedCreatedStatus(response)
        self.assertTrue('/users/{pk}'.format(pk=user.pk) in response['Location'])

        data = response.data
        self.assertEquals(data['id'], user.pk)
        self.assertEquals(data['email'], user.email)

    def test_create_user_missing_email(self):
        post_data = self.VALID_USER_DATA.copy()
        del post_data['email']
        response = self.client.post('/users/', data=post_data)
        self.assertAPIReturnedValidationErrorStatus(response)
        self.assertAPIValidationErrorHasKey(response, 'email')

    def test_create_user_extra_param(self):
        post_data = self.VALID_USER_DATA.copy()
        post_data['extra_freld'] = 'testing'
        response = self.client.post('/users/', data=post_data)

        self.assertAPIReturnedCreatedStatus(response)

    # def test_invalid_username_fails(self):
    #     post_data = self.VALID_USER_DATA
    #     post_data['username'] = 'no'

    #     response = self.client.post('/users/', data=post_data)
    #     self.assertAPIReturnedValidationErrorStatus(response)
    #     self.assertAPIValidationErrorHasKey(response, 'handle')

    def test_missing_display_name_fails(self):
        post_data = self.VALID_USER_DATA
        del post_data['display_name']

        response = self.client.post('/users/', data=post_data)
        self.assertAPIReturnedValidationErrorStatus(response)
        self.assertAPIValidationErrorHasKey(response, 'display_name')

    def test_duplicate_email_fails(self):
        User.objects.create(**self.VALID_USER_DATA)

        post_data = self.VALID_USER_DATA.copy()

        response = self.client.post('/users/', data=post_data)
        self.assertAPIReturnedValidationErrorStatus(response)
        self.assertAPIValidationErrorHasKey(response, 'email')

    def test_duplicate_username_fails(self):
        User.objects.create(**self.VALID_USER_DATA)

        post_data = self.VALID_USER_DATA.copy()
        post_data['email'] += '1'
        response = self.client.post('/users/', data=post_data)
        self.assertAPIReturnedValidationErrorStatus(response)
        self.assertAPIValidationErrorHasKey(response, 'username')


class OAuth2UserAPITestCase(APITestsBase):
    VALID_USER_DATA = {
        'email': 'test@example.com',
        'display_name': 'Test User',
        'username': '@username',
        'password': 'password'
    }
    OAUTH2_URL = '/o/token/'

    def get_auth_header(self, app):
        return self.get_auth_headers_raw(app.client_id, app.client_secret)

    def get_auth_headers_raw(self, id, secret):
        return {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(id + ':' + secret),
        }

    def user_data2auth_data(self, user):
        return {'grant_type': 'password', 'username': user['email'], 'password': user['password']}

    def get_application(self):
        user = User.objects.create_user(**self.VALID_USER_DATA)
        app = Application.objects.create(user=user,
                                         client_type=Application.CLIENT_CONFIDENTIAL,
                                         authorization_grant_type=Application.GRANT_PASSWORD)
        return app, user

    ############### OAuth2.0 tests ###############

    def test_create_application(self):
        app, user = self.get_application()
        self.assertFalse(app.client_id == '')
        self.assertFalse(app.client_secret == '')

    def test_unsupported_grant_type(self):
        app, user = self.get_application()
        response = self.client.post(self.OAUTH2_URL, self.get_auth_header(app))
        self.assertAPIValidationErrorHasKey(response, "unsupported_grant_type")

    def test_user_get_token_after_registration(self):
        app, user = self.get_application()
        data=self.user_data2auth_data(self.VALID_USER_DATA)
        response = self.client.post(self.OAUTH2_URL, data=data, **self.get_auth_header(app))
        data = response.data
        self.assertAPIReturnedKey(response, 'token_type', 'Bearer')
        self.assertIsNotNone(data['access_token'])
        self.assertIsNotNone(data['refresh_token'])
        self.assertIsNotNone(data['expires_in'])
        self.assertIsNotNone(data['scope'])

    ############### OAuth2.0 tests ###############

    def test_anonymous_cannot_access_secret(self):
        response = self.client.get('/users/secret', follow=True)
        self.assertAPIReturnedPermissionDenied(response)

    def test_user_can_access_secret(self):
        response = self.client.get('/users/secret', follow=True)
        # TODO: implement me
        # self.assertAPIReturnedKey(response, 'status', 'success')
