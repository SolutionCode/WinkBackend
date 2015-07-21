from json import loads, dumps
from django.test import TestCase

from users.models import User

class UserAPITestCase(TestCase):
    USERNAME = 'test@example.com'

    def test_get_existing_user(self):
        user = User.objects.create(username=self.USERNAME)

        response = self.client.get('/users/{pk}'.format(pk=user.pk), follow=True)

        self.assertEquals(response.status_code, 200)
        data = loads(response.content)
        self.assertEquals(data['id'], user.pk)
        self.assertEquals(data['username'], user.username)

    def test_get_not_existing_user(self):
        response = self.client.get('/users/1', follow=True)

        self.assertEquals(response.status_code, 404)

    def test_create_user(self):
        valid_user_data = {
            'username': self.USERNAME
        }
        response = self.client.post('/users/', data=dumps(valid_user_data), content_type='application/json')

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response['Location'], '/users/1/')

    def test_create_user_missing_username(self):
        valid_user_data = {}
        response = self.client.post('/users/', data=dumps(valid_user_data), content_type='application/json')

        self.assertEquals(response.status_code, 422)

    def test_create_user_extra_param(self):
        valid_user_data = {
            'extra': 'some value',
            'username': self.USERNAME
        }
        response = self.client.post('/users/', data=dumps(valid_user_data), content_type='application/json')

        self.assertEquals(response.status_code, 201)