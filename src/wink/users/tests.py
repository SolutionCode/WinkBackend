# -*- coding: UTF-8 -*-
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

    ############### OAuth2.0 tests ###############

    def test_create_application(self):
        '''
        application id and secret should be not empty after calling constructor
        '''
        self.assertFalse(self.app.client_id == '')
        self.assertFalse(self.app.client_secret == '')

    def test_unsupported_grant_type(self):
        """
        user should provide grant_type = password during loing
        maybe more test are needed
        """
        response = self.client.post(self.OAUTH2_URL)
        self.assertAPIValidationErrorHasKey(response, "unsupported_grant_type")

    def test_user_get_token_after_login(self):
        '''
        user should get token after successful login
        '''
        self.get_valid_user()
        response = self.login(self.VALID_USER_DATA)
        data = response.data

    def test_user_login_with_invalid_credentials(self):
        '''
        test if user cannot login if he doesn't exist in database
        '''
        response = self.login(self.VALID_USER_DATA)
        self.assertAPIValidationErrorHasKey(response, "invalid_grant")

    ############### OAuth2.0 tests ###############

    def test_anonymous_cannot_access_secret(self):
        '''
        it's required to login to get access to secret page
        '''
        response = self.client.get('/users/secret', follow=True)
        self.assertAPIReturnedUnauthorized(response)

    def test_user_can_access_secret(self):
        '''
        after successful login user can
        very useful for testing logging
        '''
        self.get_valid_user()
        self.login_persistent_with_json(self.VALID_USER_DATA)
        response = self.client.get('/users/secret', follow=True)
        self.assertEquals(response.data['status'], 'success')


class FacebookTestCase(APITestClientLogin):
    '''
    facebook api login & registration
    '''

    # token should be valid till October 22nd, However facebook can revoke access
    EXTENDED_FACEBOOK_TOKEN1 = "CAAUshhSyCnEBAIXwDP2osd01os2pO0bKUoSgdkVxiiaZBdS1KBs8lZBO3ZCNFsWB7RPyTVuY0V6A4NnmeL2e1kYzexukL0TiCK3H3PzW2oSC0SYMYVHorXQIF8DquPipRhzhLJsixEOQNGsUw0clHVIHSByxQ2apuZA7jmB976dzyhK7CvnL6rptiyI7tCYZD"
    EXTENDED_FACEBOOK_TOKEN2 = "CAAUshhSyCnEBAPaxXFXwG2UaEWuEe6mkkU9o7pXNJZCTlSMP1J5kHEnPL1tSODbLE75jZBlv1mC3c4zrXfewKT7eIi26cqbce1IFv5k7oSGCYYwZCOWMEAoIEYVrQyfo6qs3t2cVDZCCxStCwrU2keQKhVouzKL9RfYlPzD65Dm2JAf8hwxF37FuzWKZBQg4ZD"
    INVALID_FACEBOOK_TOKEN = "1"
    REGISTRATION_URL = "/users/register-social/facebook/{token}/"
    LOGIN_URL = "/users/login-social/facebook/{token}/"

    FACEBOOK_USER_DATA = {
        'email': 'sacherus@gmail.com',
        'display_name': '',
        # 'username': 'Piotr Józef Kowenzowski',
    }

    def __compare_user2json(self, user, json):
        self.assertEquals(user.display_name, self.FACEBOOK_USER_DATA['email'])
        self.assertEquals(user.email, self.FACEBOOK_USER_DATA['email'])
        self.assertEquals(user.username, self.FACEBOOK_USER_DATA['username'])

    def test_user_signup(self):
        '''
        sent token and check if user is registered in database
        '''
        response = self.client.get(self.REGISTRATION_URL.format(token=self.EXTENDED_FACEBOOK_TOKEN1))
        user = User.objects.get(pk=2)
        self.check_valid_token(response.data)

    def test_user_signin(self):
        '''
        sent token and check if user is returne
        '''
        response = self.client.get(self.LOGIN_URL.format(token=self.EXTENDED_FACEBOOK_TOKEN1))
        self.check_valid_token(response.data)

    def test_user_signup_and_signin(self):
        '''
        sent token, register, and then login using different token, pretty simple? :)
        '''
        response = self.client.get(self.REGISTRATION_URL.format(token=self.EXTENDED_FACEBOOK_TOKEN1))
        self.check_valid_token(response.data)
        response = self.client.get(self.LOGIN_URL.format(token=self.EXTENDED_FACEBOOK_TOKEN2))
        self.check_valid_token(response.data)

    def test_user_signup_twice(self):
        '''
        sent token, register, and then login using different token, pretty simple? :)
        '''
        response = self.client.get(self.REGISTRATION_URL.format(token=self.EXTENDED_FACEBOOK_TOKEN1))
        self.check_valid_token(response.data)
        response = self.client.get(self.REGISTRATION_URL.format(token=self.EXTENDED_FACEBOOK_TOKEN1))
        self.assertAPIValidationErrorHasKey(response, "user already registered")

    def test_app_sent_invalid_token_registration(self):
        '''
        application sents invalid token...
        '''
        response = self.client.get(self.REGISTRATION_URL.format(token=self.INVALID_FACEBOOK_TOKEN))
        self.assertAPIValidationErrorHasKey(response, "invalid facebook token")

    def test_app_sent_invalid_token_login(self):
        '''
        application sents invalid token...
        '''
        response = self.client.get(self.LOGIN_URL.format(token=self.INVALID_FACEBOOK_TOKEN))
        self.assertAPIValidationErrorHasKey(response, "invalid facebook token")
