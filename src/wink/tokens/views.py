import json

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import login
from django.http import JsonResponse
from requests import HTTPError
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from social.apps.django_app.utils import psa
from oauth2_provider.views import TokenView
from tools import get_access_token
from users.serializers import UserSerializer


class WinkTokenView(TokenView):
    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):
        '''
        extended OAuth token view, because error should be changed to errors
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        url, headers, body, status = self.create_token_response(request)
        d = json.loads(body)
        if 'error' in d:
            d['errors'] = d['error']
            del d['error']
        body = json.dumps(d)
        response = HttpResponse(content=body, status=status)
        for k, v in headers.items():
            response[k] = v
        return response


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
