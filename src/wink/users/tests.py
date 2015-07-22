from json import loads, dumps
from django.test import TestCase

from users.models import User


class UserModelTests(TestCase):

    def test_invalid_handle(self):
        pass

class UserAPITestCase(TestCase):
    EMAIL = 'test@example.com'
    HANDLE = '@test'
    FIRST_NAME = 'Test'
    LAST_NAME = 'User'
    PASSWORD = 'test'

    def test_get_existing_user(self):
        user = User.objects.create(email=self.EMAIL)

        response = self.client.get('/users/{pk}'.format(pk=user.pk), follow=True)

        self.assertEquals(response.status_code, 200)
        data = loads(response.content)
        self.assertEquals(data['id'], user.pk)
        self.assertEquals(data['email'], user.email)

    def test_get_not_existing_user(self):
        response = self.client.get('/users/1', follow=True)

        self.assertEquals(response.status_code, 404)

    def test_create_user(self):
        valid_user_data = {
            'email': self.EMAIL,
            'first_name': self.FIRST_NAME,
            'last_name': self.LAST_NAME,
            'handle': self.HANDLE,
            'password': self.PASSWORD
        }
        response = self.client.post('/users', data=dumps(valid_user_data), content_type='application/json')

        self.assertEquals(response.status_code, 201)
        self.assertTrue('/users/1' in response['Location'])

    def test_create_user_missing_username(self):
        valid_user_data = {}
        response = self.client.post('/users', data=dumps(valid_user_data), content_type='application/json')

        self.assertEquals(response.status_code, 422)

    def test_create_user_extra_param(self):
        valid_user_data = {
            'email': self.EMAIL,
            'first_name': self.FIRST_NAME,
            'last_name': self.LAST_NAME,
            'handle': self.HANDLE,
            'password': self.PASSWORD,

            'extra': 'something extra'
        }
        response = self.client.post('/users', data=dumps(valid_user_data), content_type='application/json')

        self.assertEquals(response.status_code, 201)