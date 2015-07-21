from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer
from restless.exceptions import HttpError

from users.models import User


class UserResource(DjangoResource):
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'username': 'username'
    })

    def is_authenticated(self):
        return True

    def detail(self, pk):
        return User.objects.get(pk=pk)

    def create(self):
        if not self.data.get('username'):
            # TODO: wrap in helper
            e = HttpError('username is not provided')
            e.status = 422
            raise e

        return User.objects.create(**self.data)

