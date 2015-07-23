from json import dumps, loads
from restless.preparers import FieldsPreparer
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound
from django.core.urlresolvers import reverse

from common.http import HttpResponseCreated, HttpResponseEntityCouldNotBeProcessed
from users.models import User
from users.forms import UserForm


user_fields_preparer = FieldsPreparer(
    {
        'id': 'id',
        'handle': 'handle',
        'email': 'email'
    }
)


def user_detail(request, pk):
    if request.method == 'GET':
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return HttpResponseNotFound()

        data = user_fields_preparer.prepare(user)
        return HttpResponse(dumps(data))

    return HttpResponseNotAllowed(permitted_methods=['GET'])


def users_list(request):
    if request.method == 'POST':
        user_form = UserForm(loads(request.body))
        if not user_form.is_valid():
            return HttpResponseEntityCouldNotBeProcessed(dumps({'errors': user_form.errors}))

        user = user_form.save()
        data = user_fields_preparer.prepare(user)
        response = HttpResponseCreated(dumps(data))
        response['Location'] = reverse('usersK-detail', args=[user.pk])
        return response

    return HttpResponseNotAllowed(permitted_methods=['POST'])