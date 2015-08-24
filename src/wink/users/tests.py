from common.test_utils import APITestClientLogin
from users.models import User


class GetUserAPITestCase(APITestClientLogin):
    VALID_USER_DATA = {
        'email': 'test@example.com',
        'display_name': 'Test User',
        'username': '@username',
        'password': 'password'
    }

    def test_get_existing_user(self):
        user = self.get_valid_user()
        self.login_persistent_with_json(self.VALID_USER_DATA)

        response = self.client.get('/users/{pk}'.format(pk=user.pk), follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data
        self.assertEquals(data['id'], user.pk)
        self.assertEquals(data['email'], user.email)

    def test_get_user_not_authorized(self):
        user = self.get_valid_user()
        # self.login_persistent_with_json(self.VALID_USER_DATA)

        response = self.client.get('/users/{pk}'.format(pk=user.pk), follow=True)

        self.assertAPIReturnedUnauthorized(response)


class UpdateUserAPITestCase(APITestClientLogin):
    VALID_USER_DATA = {
        'email': 'test@example.com',
        'display_name': 'Test User',
        'username': '@username',
        'password': 'password'
    }

    def test_patch_not_authorized_user(self):
        user = self.get_valid_user()
        # self.login_persistent_with_json(self.VALID_USER_DATA)

        response = self.client.patch('/users/{pk}'.format(pk=user.pk), follow=True)
        self.assertAPIReturnedUnauthorized(response)

    def test_patch_display_name_successful(self):
        user = self.get_valid_user()
        self.login_persistent_with_json(self.VALID_USER_DATA)

        patched_display_name = 'New Display Name'
        response = self.client.patch('/users/{pk}'.format(pk=user.pk),
                                     data={'display_name': patched_display_name},
                                     follow=True)
        self.assertAPIReturnedOKStatus(response)

        user = User.objects.get(pk=user.pk)
        self.assertEquals(user.display_name, patched_display_name)

    def test_patch_username_uniqueness(self):
        other_user = User.objects.create(username='SomeUser', email='other@example.com')
        user = self.get_valid_user()
        self.login_persistent_with_json(self.VALID_USER_DATA)

        patched = other_user.username
        response = self.client.patch('/users/{pk}'.format(pk=user.pk),
                                     data={'username': patched},
                                     follow=True)
        self.assertAPIReturnedValidationErrorStatus(response)
        self.assertAPIValidationErrorHasKey(response, 'username')

    def test_put_not_supported(self):
        user = self.get_valid_user()
        self.login_persistent_with_json(self.VALID_USER_DATA)

        response = self.client.put('/users/{pk}'.format(pk=user.pk), follow=True)
        self.assertAPIReturnedMethodNotSupportedStatus(response)