from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth import login
from django.http import JsonResponse
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

# When we send a third party access token to that view
# as a GET request with access_token parameter, 
# python social auth communicate with
# the third party and request the user info to register or
# sign in the user. Magic. Yeah.
@psa('social:complete')
def register_by_access_token(request, backend):
 
    token = request.GET.get('access_token')
    # here comes the magic
    user = request.backend.do_auth(token)
    if user:
        login(request, user)
        # that function will return our own
        # OAuth2 token as JSON
        return get_access_token(user)
    else:
        # If there was an error... you decide what you do here
        return HttpResponse("error")


def logout_view(request):
    logout(request)
    # Redirect to a success page.


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def secret(request, *args, **kwargs):
    return JsonResponse({'status': 'success'})