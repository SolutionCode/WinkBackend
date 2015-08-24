from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED
from django.contrib.auth import logout
from django.http import JsonResponse

from users.models import User
from users.serializers import UserSerializer


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', 'options']

    permission_classes = (IsAuthenticated,)


def logout_view(request):
    '''
    testing purpuse only
    :param request:
    :return:
    '''
    logout(request)
    # Redirect to a success page.


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def secret(request, *args, **kwargs):
    '''
    testing purpuse only
    :param request:
    :return:
    '''
    return JsonResponse({'status': 'success'})
