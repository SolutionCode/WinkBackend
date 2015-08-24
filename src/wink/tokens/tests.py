# -*- coding: UTF-8 -*-
from common.test_utils import APITestClientLogin
from users.models import User

# Create your tests here.

class OAuth2UserAPITestCase(APITestClientLogin):
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

    # EXTENDED_FACEBOOK_TOKEN1 = {
    #     'backend': 'facebook',
    #     'social_token': "CAAUshhSyCnEBAIXwDP2osd01os2pO0bKUoSgdkVxiiaZBdS1KBs8lZBO3ZCNFsWB7RPyTVuY0V6A4NnmeL2e1kYzexukL0TiCK3H3PzW2oSC0SYMYVHorXQIF8DquPipRhzhLJsixEOQNGsUw0clHVIHSByxQ2apuZA7jmB976dzyhK7CvnL6rptiyI7tCYZD}"}
    # EXTENDED_FACEBOOK_TOKEN2 = {
    #     'backend': 'facebook',
    #     'social_token': "CAAUshhSyCnEBAPaxXFXwG2UaEWuEe6mkkU9o7pXNJZCTlSMP1J5kHEnPL1tSODbLE75jZBlv1mC3c4zrXfewKT7eIi26cqbce1IFv5k7oSGCYYwZCOWMEAoIEYVrQyfo6qs3t2cVDZCCxStCwrU2keQKhVouzKL9RfYlPzD65Dm2JAf8hwxF37FuzWKZBQg4ZD"}
    # INVALID_FACEBOOK_TOKEN = {'backend': 'facebook', 'social_token': "1"}

    EXTENDED_FACEBOOK_TOKEN1 = "CAAUshhSyCnEBAIXwDP2osd01os2pO0bKUoSgdkVxiiaZBdS1KBs8lZBO3ZCNFsWB7RPyTVuY0V6A4NnmeL2e1kYzexukL0TiCK3H3PzW2oSC0SYMYVHorXQIF8DquPipRhzhLJsixEOQNGsUw0clHVIHSByxQ2apuZA7jmB976dzyhK7CvnL6rptiyI7tCYZD"
    EXTENDED_FACEBOOK_TOKEN2 = "CAAUshhSyCnEBAPaxXFXwG2UaEWuEe6mkkU9o7pXNJZCTlSMP1J5kHEnPL1tSODbLE75jZBlv1mC3c4zrXfewKT7eIi26cqbce1IFv5k7oSGCYYwZCOWMEAoIEYVrQyfo6qs3t2cVDZCCxStCwrU2keQKhVouzKL9RfYlPzD65Dm2JAf8hwxF37FuzWKZBQg4ZD"
    INVALID_FACEBOOK_TOKEN = "1"

    REGISTRATION_URL = "/tokens/social/register/"
    LOGIN_URL = "/tokens/social/login/"

    FACEBOOK_USER_DATA = {
        'email': 'sacherus@gmail.com',
        'display_name': '',
        # 'username': 'Piotr Józef Kowenzowski',
    }

    def setUp(self):
        super(FacebookTestCase, self).setUp()
        self.EXTENDED_FACEBOOK_TOKEN1 = self.__token2dict(self.EXTENDED_FACEBOOK_TOKEN1)
        self.EXTENDED_FACEBOOK_TOKEN2 = self.__token2dict(self.EXTENDED_FACEBOOK_TOKEN2)
        self.INVALID_FACEBOOK_TOKEN = self.__token2dict(self.INVALID_FACEBOOK_TOKEN)


    def __compare_user2json(self, user, json):
        self.assertEquals(user.display_name, self.FACEBOOK_USER_DATA['email'])
        self.assertEquals(user.email, self.FACEBOOK_USER_DATA['email'])
        self.assertEquals(user.username, self.FACEBOOK_USER_DATA['username'])

    def __token2dict(self, token):
        return {'backend': 'facebook', 'social_token': token, 'client_id': self.app.client_id,
                'client_secret': self.app.client_secret}

    def test_user_signup(self):
        '''
        sent token and check if user is registered in database
        '''
        response = self.client.post(self.REGISTRATION_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        user = User.objects.get(pk=2)
        self.check_valid_token(response.data)

    def test_user_signin(self):
        '''
        sent token and check if user is returne
        '''
        response = self.client.post(self.LOGIN_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.check_valid_token(response.data)

    def test_user_signup_and_signin(self):
        '''
        sent token, register, and then login using different token, pretty simple? :)
        '''
        response = self.client.post(self.REGISTRATION_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.check_valid_token(response.data)
        response = self.client.post(self.LOGIN_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.check_valid_token(response.data)

    def test_user_signup_twice(self):
        '''
        sent token, register, and then login using different token, pretty simple? :)
        '''
        response = self.client.post(self.REGISTRATION_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.check_valid_token(response.data)
        response = self.client.post(self.REGISTRATION_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.assertAPIValidationErrorHasKey(response, "user already registered")

    def test_app_sent_invalid_token_registration(self):
        '''
        application sents invalid token...
        '''
        response = self.client.post(self.REGISTRATION_URL, data=self.INVALID_FACEBOOK_TOKEN)
        print response
        self.assertAPIValidationErrorHasKey(response, "400 Client Error: Bad Request when connecting to facebook")

    def test_app_sent_invalid_token_login(self):
        '''
        application sents invalid token...
        '''
        response = self.client.post(self.LOGIN_URL, data=self.INVALID_FACEBOOK_TOKEN)
        self.assertAPIValidationErrorHasKey(response, "400 Client Error: Bad Request when connecting to facebook")
