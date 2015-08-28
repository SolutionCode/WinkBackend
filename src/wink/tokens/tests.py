from common.test_utils import APITestsBase
from users.models import User

# Create your tests here.

class OAuth2UserAPITestCase(APITestsBase):
    def test_create_application(self):
        '''
        application id and secret should be not empty after calling constructor
        '''
        self.assertFalse(self.app.client_id == '')
        self.assertFalse(self.app.client_secret == '')
        # TODO: tests should not check setup logic

    def test_unsupported_grant_type(self):
        """
        user should provide grant_type = password during loing
        maybe more test are needed
        """
        response = self.client.post(self.OAUTH2_TOKEN_URL)
        self.assertAPIValidationErrorHasKey(response, "unsupported_grant_type")

    def test_user_get_token_after_login(self):
        '''
        user should get token after successful login
        '''
        user = self.create_user()
        response = self.login(user)
        self.check_valid_token(response.data)

    def test_user_login_with_invalid_credentials(self):
        '''
        test if user cannot login if he doesn't exist in database
        '''
        user = User()
        user.email = 'fake@example.com'
        data = self._user_data2auth_data(user)
        response = self.client.post_with_auth_header(self.OAUTH2_TOKEN_URL, data=data)
        self.assertAPIValidationErrorHasKey(response, "invalid_grant")

    def test_anonymous_cannot_access_secret(self):
        '''
        it's required to login to get access to secret page
        '''
        response = self.client.get('/tokens/secret', follow=True)
        self.assertAPIReturnedUnauthorized(response)

    def test_user_can_access_secret(self):
        '''
        after successful login user can
        very useful for testing logging
        '''
        user = self.create_user()
        self.login(user)
        response = self.client.get('/tokens/secret', follow=True)
        self.assertEquals(response.data['status'], 'success')

    def test_authenticated_request_has_user(self):
        '''
        after successful login user can
        very useful for testing logging
        '''
        user = self.create_user()
        self.login(user)
        response = self.client.get('/tokens/secret', follow=True)
        self.assertEquals(response.data['user'], user.pk)

    def test_user_logout_by_revoking_token(self):
        '''
        POST /o/revoke_token/ HTTP/1.1
        Content-Type: json
        {token: token=XXXX}; client_id=XXXX&client_secret=XXXX in authheader
        The server will respond wih a 200 status code on successful revocation.
        '''
        user = self.create_user()
        self.login(user)
        response = self.client.get('/tokens/secret', follow=True)
        self.assertEquals(response.data['status'], 'success')
        response = self.logout()
        self.assertAPIReturnedOKStatus(response)
        response = self.client.get('/tokens/secret', follow=True)
        self.assertAPIReturnedUnauthorized(response)

    def test_user_extends_his_token(self):
        user = self.create_user()
        self.login(user)
        token1 = self.client.token
        response = self.client.get('/tokens/secret', follow=True)
        self.assertEquals(response.data['status'], 'success')
        self.extend_login()
        token2 = self.client.token
        response = self.client.get('/tokens/secret', follow=True)
        self.assertEquals(response.data['status'], 'success')
        self.client.token = token1
        response = self.client.get('/tokens/secret', follow=True)
        self.assertAPIReturnedUnauthorized(response)


class FacebookTestCase(APITestsBase):
    '''
    facebook api login & registration
    '''

    # token should be valid till October 22nd, However facebook can revoke access
    EXTENDED_FACEBOOK_TOKEN1 = "CAAUshhSyCnEBAIXwDP2osd01os2pO0bKUoSgdkVxiiaZBdS1KBs8lZBO3ZCNFsWB7RPyTVuY0V6A4NnmeL2e1kYzexukL0TiCK3H3PzW2oSC0SYMYVHorXQIF8DquPipRhzhLJsixEOQNGsUw0clHVIHSByxQ2apuZA7jmB976dzyhK7CvnL6rptiyI7tCYZD"
    EXTENDED_FACEBOOK_TOKEN2 = "CAAUshhSyCnEBAPaxXFXwG2UaEWuEe6mkkU9o7pXNJZCTlSMP1J5kHEnPL1tSODbLE75jZBlv1mC3c4zrXfewKT7eIi26cqbce1IFv5k7oSGCYYwZCOWMEAoIEYVrQyfo6qs3t2cVDZCCxStCwrU2keQKhVouzKL9RfYlPzD65Dm2JAf8hwxF37FuzWKZBQg4ZD"
    INVALID_FACEBOOK_TOKEN = "1"

    REGISTRATION_URL = "/tokens/social/register/"
    LOGIN_URL = "/tokens/social/login/"

    FACEBOOK_USER_DATA = {
        'email': 'sacherus@gmail.com',
        'display_name': u'Piotr J\xf3zef Kowenzowski',
        'username': '@piotrjozefkowenzowski',
    }

    def setUp(self):
        super(FacebookTestCase, self).setUp()
        self.EXTENDED_FACEBOOK_TOKEN1 = self.__token2dict(self.EXTENDED_FACEBOOK_TOKEN1)
        self.EXTENDED_FACEBOOK_TOKEN2 = self.__token2dict(self.EXTENDED_FACEBOOK_TOKEN2)
        self.INVALID_FACEBOOK_TOKEN = self.__token2dict(self.INVALID_FACEBOOK_TOKEN)

    def __compare_user2json(self, user, data):
        self.assertEquals(user.display_name, data['display_name'])
        self.assertEquals(user.email, data['email'])
        self.assertEquals(user.username, data['username'])

    def __token2dict(self, token):
        return {'backend': 'facebook', 'social_token': token}

    def test_user_signup_db(self):
        '''
        sent token and check if user is registered in database
        '''
        response = self.client.post_with_auth_header(self.REGISTRATION_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        user = User.objects.get(pk=2)
        self.__compare_user2json(user, self.FACEBOOK_USER_DATA)
        self.check_valid_token(response.data)

    def test_user_signin(self):
        '''
        sent token and check if user is returned
        '''
        response = self.client.post_with_auth_header(self.LOGIN_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.check_valid_token(response.data)

    def test_user_signup_and_signin(self):
        '''
        sent token, register, and then login using different token, pretty simple? :)
        '''
        response = self.client.post_with_auth_header(self.REGISTRATION_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.check_valid_token(response.data)
        response = self.client.post_with_auth_header(self.LOGIN_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.check_valid_token(response.data)

    def test_user_signup_response(self):
        '''
        sent token, register, and then login using different token, pretty simple? :)
        '''
        response = self.client.post_with_auth_header(self.REGISTRATION_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.check_valid_token(response.data)
        facebook_set = set(self.FACEBOOK_USER_DATA.items())
        response_set = set(response.data['data']['user'].items())
        self.assertTrue(facebook_set.issubset(response_set),
                        "Got real data from facebook in response after registration")

    def test_user_signup_twice(self):
        '''
        sent token, register, and then login using different token, pretty simple? :)
        '''
        response = self.client.post_with_auth_header(self.REGISTRATION_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.check_valid_token(response.data)
        response = self.client.post_with_auth_header(self.REGISTRATION_URL, data=self.EXTENDED_FACEBOOK_TOKEN1)
        self.assertAPIValidationErrorHasKey(response, "user already registered")

    def test_app_sent_invalid_token_registration(self):
        '''
        application sents invalid token...
        '''
        response = self.client.post_with_auth_header(self.REGISTRATION_URL, data=self.INVALID_FACEBOOK_TOKEN)
        self.assertAPIValidationErrorHasKey(response, "400 Client Error: Bad Request when connecting to facebook")

    def test_app_sent_invalid_token_login(self):
        '''
        application sents invalid token...
        '''
        response = self.client.post_with_auth_header(self.LOGIN_URL, data=self.INVALID_FACEBOOK_TOKEN)
        self.assertAPIValidationErrorHasKey(response, "400 Client Error: Bad Request when connecting to facebook")
