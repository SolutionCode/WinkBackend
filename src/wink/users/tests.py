from json import loads, dumps
from django.test import TestCase

from users.models import User


class UserModelTests(TestCase):

    def test_invalid_handle(self):
        pass

class UserAPITestCase(TestCase):
    VALID_USER_DATA = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
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
        response = self.client.post('/users', data=dumps(self.VALID_USER_DATA), content_type='application/json')

        self.assertEquals(response.status_code, 201)
        self.assertTrue('/users/1' in response['Location'])

    def test_create_user_missing_email(self):
        post_data = self.VALID_USER_DATA.copy()
        del post_data['email']
        response = self.client.post('/users', data=dumps(post_data), content_type='application/json')

        self.assertEquals(response.status_code, 422)
        data = loads(response.content)
        self.assertTrue('email' in data['errors'])

    def test_create_user_extra_param(self):
        post_data = self.VALID_USER_DATA.copy()
        post_data['extra_freld'] = 'testing'
        response = self.client.post('/users', data=dumps(post_data), content_type='application/json')

        self.assertEquals(response.status_code, 201)

    def test_invalid_handle_fails(self):
        post_data = self.VALID_USER_DATA
        post_data['handle'] = 'no'

        response = self.client.post('/users', data=dumps(post_data), content_type='application_json')
        self.assertEquals(response.status_code, 422)
        data = loads(response.content)
        self.assertTrue('handle' in data['errors'])