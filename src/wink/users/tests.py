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


from oauth2_provider.models import Application
class OAuth2UserAPITestCase(APITestsBase):
    VALID_USER_DATA = {
        'email': 'test@example.com',
        'display_name': 'Test User',
        'username': '@username',
        'password': 'password'
    }

    def create_application(self):
        instance = User.objects.create(**self.VALID_USER_DATA)
        return Application.objects.create(user=instance, 
                                   client_type=Application.CLIENT_CONFIDENTIAL,
                                   authorization_grant_type=Application.GRANT_PASSWORD)

    def test_create_application(self):
        app = self.create_application()
        self.assertFalse(app.client_id == '')
        self.assertFalse(app.client_secret == '')

    def test_wrong_client_id(self):
        app = self.create_application()