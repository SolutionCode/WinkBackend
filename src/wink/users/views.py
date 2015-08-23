from requests import HTTPError
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import logout
from django.contrib.auth import login
from django.http import JsonResponse
from rest_framework.response import Response
from social.apps.django_app.utils import psa

from users.tools import get_access_token
from users.models import User
from users.serializers import UserSerializer


class UserCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer



def __facebook_login_error():
    return Response({"errors": "invalid facebook token"}, status=status.HTTP_401_UNAUTHORIZED)

# When we send a third party access token to that view
# as a GET request with access_token parameter, 
# python social auth communicate with
# the third party and request the user info to register or
# sign in the user. Magic. Yeah.
@api_view(['GET'])
@psa('social:complete')
def register_by_access_token(request, backend, token, *args, **kwargs):
    try:
        user = request.backend.do_auth(token)
        if user:
            if not user.last_login:
                login(request, user)
                returned_json = get_access_token(user)
                serializer = UserSerializer(user, context={'request': request})
                returned_json.update(serializer.data)
                return JsonResponse(returned_json)
            else:
                return Response({"errors": "user already registered"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return __facebook_login_error();
    except HTTPError:
        return __facebook_login_error();

@api_view(['GET'])
@psa('social:complete')
def login_by_access_token(request, backend, token, *args, **kwargs):
    try:
        user = request.backend.do_auth(token)
        if user:
            login(request, user)
            returned_json = get_access_token(user)
            return JsonResponse(returned_json)
        else:
           return __facebook_login_error()
    except HTTPError:
        return __facebook_login_error()


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
