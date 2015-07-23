from json import loads, dumps

from common.test_utils import APITestsBase
from users.models import User



class UserAPITestCase(APITestsBase):
    VALID_USER_DATA = {
        'email': 'test@example.com',
        'display_name': 'Test User',
        'handle': '@handle',
        'password': 'password'
    }

    def test_get_existing_user(self):
        user = User.objects.create(email=self.VALID_USER_DATA['email'])

        response = self.client.get('/users/{pk}'.format(pk=user.pk), follow=True)

        self.assertEquals(response.status_code, 200)
        data = loads(response.content)
        self.assertEquals(data['id'], user.pk)
        self.assertEquals(data['email'], user.email)

    def test_get_not_existing_user(self):
        response = self.client.get('/users/1', follow=True)

        self.assertEquals(response.status_code, 404)

    def test_create_user(self):
        response = self.client.post('/users', data=self.VALID_USER_DATA)

        self.assertEquals(User.objects.count(), 1)
        user = User.objects.first()

        self.assertEquals(response.status_code, 201)
        self.assertTrue('/users/{pk}'.format(pk=user.pk) in response['Location'])

    def test_create_user_missing_email(self):
        post_data = self.VALID_USER_DATA.copy()
        del post_data['email']
        response = self.client.post('/users', data=post_data)

        self.assertEquals(response.status_code, 422)
        data = loads(response.content)
        self.assertTrue('email' in data['errors'])

    def test_create_user_extra_param(self):
        post_data = self.VALID_USER_DATA.copy()
        post_data['extra_freld'] = 'testing'
        response = self.client.post('/users', data=post_data)

        self.assertEquals(response.status_code, 201)

    def test_invalid_handle_fails(self):
        post_data = self.VALID_USER_DATA
        post_data['handle'] = 'no'

        response = self.client.post('/users', data=post_data)
        self.assertEquals(response.status_code, 422)
        data = loads(response.content)
        self.assertTrue('handle' in data['errors'])

    def test_missing_display_name_fails(self):
        post_data = self.VALID_USER_DATA
        del post_data['display_name']

        response = self.client.post('/users', data=post_data)
        self.assertEquals(response.status_code, 422)
        data = loads(response.content)
        self.assertTrue('display_name' in data['errors'])