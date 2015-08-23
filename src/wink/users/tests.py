from oauth2_provider.models import Application
from common.test_utils import APITestsBase, APITestClientLogin
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


class OAuth2UserAPITestCase(APITestClientLogin):

    def test_create_application(self):
        self.assertFalse(self.app.client_id == '')
        self.assertFalse(self.app.client_secret == '')

    def test_unsupported_grant_type(self):
        response = self.client.post(self.OAUTH2_URL)
        self.assertAPIValidationErrorHasKey(response, "unsupported_grant_type")

    def test_user_get_token_after_registration(self):
        self.get_valid_user()
        response = self.login(self.VALID_USER_DATA)
        data = response.data
        self.assertAPIReturnedKey(response, 'token_type', 'Bearer')
        self.assertIsNotNone(data['access_token'])
        self.assertIsNotNone(data['refresh_token'])
        self.assertIsNotNone(data['expires_in'])
        self.assertIsNotNone(data['scope'])

    def test_user_login_with_invalid_credentials(self):
        response = self.login(self.VALID_USER_DATA)
        self.assertAPIValidationErrorHasKey(response, "invalid_grant")

    ############### OAuth2.0 tests ###############

    def test_anonymous_cannot_access_secret(self):
        response = self.client.get('/users/secret', follow=True)
        self.assertAPIReturnedUnauthorized(response)

    def test_user_can_access_secret(self):
        self.get_valid_user()
        self.login_persistent(self.VALID_USER_DATA)
        response = self.client.get('/users/secret', follow=True)
        self.assertEquals(response.data['status'], 'success')