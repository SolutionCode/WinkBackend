from common.test_utils import APITestClientLogin, APITestsBase
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
        data = response.data['data']['user']
        self.assertEquals(data['id'], user.pk)
        self.assertEquals(data['email'], user.email)
        self.assertEquals(data['username'], user.username)
        self.assertEquals(data['display_name'], user.display_name)

    def test_get_user_not_authorized(self):
        user = self.get_valid_user()
        # self.login_persistent_with_json(self.VALID_USER_DATA)

        response = self.client.get('/users/{pk}'.format(pk=user.pk), follow=True)

        self.assertAPIReturnedUnauthorized(response)

    def test_get_other_user(self):
        other_user = User.objects.create(username='SomeUser', email='other@example.com')
        user = self.get_valid_user()
        self.login_persistent_with_json(self.VALID_USER_DATA)

        response = self.client.get('/users/{pk}'.format(pk=other_user.pk), follow=True)

        self.assertAPIReturnedForbiddenStatus(response)


class GetPublicUserAPITestCase(APITestClientLogin):

    def test_get_non_existing_user(self):
        response = self.client.get('/users/0/public', follow=True)

        self.assertAPIReturnedNotFoundStatus(response)

    def test_get_existing_user(self):
        user = self.get_valid_user()
        response = self.client.get('/users/{pk}/public'.format(pk=user.pk), follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']['user_public']
        self.assertEquals(data['id'], user.pk)
        self.assertEquals(data['username'], user.username)
        self.assertEquals(data['display_name'], user.display_name)
        self.assertFalse('email' in data)


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

    def test_patch_other_user(self):
        other_user = User.objects.create(username='SomeUser', email='other@example.com')
        user = self.get_valid_user()
        self.login_persistent_with_json(self.VALID_USER_DATA)

        patched = other_user.username
        response = self.client.patch('/users/{pk}'.format(pk=other_user.pk),
                                     data={'username': patched},
                                     follow=True)
        self.assertAPIReturnedForbiddenStatus(response)

    def test_put_not_supported(self):
        user = self.get_valid_user()
        self.login_persistent_with_json(self.VALID_USER_DATA)

        response = self.client.put('/users/{pk}'.format(pk=user.pk), follow=True)
        self.assertAPIReturnedMethodNotAllowedStatus(response)


class ListUserPublicAPITestCase(APITestsBase):

    def test_get_empty_list(self):

        response = self.client.get('/users/public', follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']
        self.assertEquals(len(data['user_public']), 0)

    def test_get_list_one_element(self):
        User.objects.create(username='@username', email='test@example.com')

        response = self.client.get('/users/public', follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']
        self.assertEquals(len(data['user_public']), 1)

    def test_pagination(self):
        for i in range(100):
            User.objects.create(username='@username' + str(i), email=str(i) + 'test@example.com')

        response = self.client.get('/users/public', follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']
        self.assertEquals(len(data['user_public']), 10)

        # check pagination object
        self.assertTrue('pagination' in data)
        self.assertEquals(data['pagination']['count'], 100)
        self.assertTrue('next' in data['pagination'])
        self.assertTrue('previous' in data['pagination'])

    def test_filtering_by_username(self):
        user_1 = User.objects.create(username='@username1', email='test+1@example.com')
        User.objects.create(username='@username2', email='test+2@example.com')

        response = self.client.get('/users/public?username={username}'.format(username=user_1.username), follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']
        self.assertEquals(len(data['user_public']), 1)
        self.assertEquals(data['user_public'][0]['id'], user_1.id)

    def test_search_by_display_name_partial(self):
        user_1 = User.objects.create(username='@username1', email='test+1@example.com', display_name='Included')
        User.objects.create(username='@username2', email='test+2@example.com', display_name='Excluded')

        response = self.client.get('/users/public?search={s}'.format(s=user_1.display_name[:-3]), follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']
        self.assertEquals(len(data['user_public']), 1)
        self.assertEquals(data['user_public'][0]['id'], user_1.id)

    def test_search_by_username_partial(self):
        user_1 = User.objects.create(username='@username1', email='test+1@example.com', display_name='Included')
        User.objects.create(username='@username2', email='test+2@example.com', display_name='Excluded')

        response = self.client.get('/users/public?search={s}'.format(s=user_1.username[1:]), follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']
        self.assertEquals(len(data['user_public']), 1)
        self.assertEquals(data['user_public'][0]['id'], user_1.id)

    def test_filtering_by_email_ignored(self):
        user_1 = User.objects.create(username='@username1', email='test+1@example.com')
        User.objects.create(username='@username2', email='test+2@example.com')

        response = self.client.get('/users/public?email={email}'.format(email=user_1.email), follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']
        self.assertEquals(len(data['user_public']), 2)

    def test_sorting_by_display_name(self):
        user_1 = User.objects.create(username='@username1', email='test+1@example.com', display_name='A')
        user_2 = User.objects.create(username='@username2', email='test+2@example.com', display_name='C')
        user_3 = User.objects.create(username='@username3', email='test+3@example.com', display_name='B')

        response = self.client.get('/users/public?ordering=display_name', follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']
        self.assertEquals(len(data['user_public']), 3)
        self.assertEquals(data['user_public'][0]['id'], user_1.id)
        self.assertEquals(data['user_public'][1]['id'], user_3.id)
        self.assertEquals(data['user_public'][2]['id'], user_2.id)

    def test_sorting_by_display_name_descending(self):
        user_1 = User.objects.create(username='@username1', email='test+1@example.com', display_name='A')
        user_2 = User.objects.create(username='@username2', email='test+2@example.com', display_name='C')
        user_3 = User.objects.create(username='@username3', email='test+3@example.com', display_name='B')

        response = self.client.get('/users/public?ordering=-display_name', follow=True)

        self.assertAPIReturnedOKStatus(response)
        data = response.data['data']
        self.assertEquals(len(data['user_public']), 3)
        self.assertEquals(data['user_public'][2]['id'], user_1.id)
        self.assertEquals(data['user_public'][1]['id'], user_3.id)
        self.assertEquals(data['user_public'][0]['id'], user_2.id)