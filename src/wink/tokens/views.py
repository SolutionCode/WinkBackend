import json

from requests import HTTPError
from social.apps.django_app.utils import load_strategy, load_backend
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import login
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from oauth2_provider.views import TokenView

from tokens.tools import get_access_token
from users.serializers import UserSerializer
from tokens.serializers import SocialTokenSerializer


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


def _facebook_login_error():
    return Response({"errors": "invalid facebook token"}, status=status.HTTP_401_UNAUTHORIZED)

# def process_social(f):
#     def decorated(request, *args, **kwargs):
#         response = f(request, *args, **kwargs)
#         print "homo"
#         return response
#
#     return decorated

# @psa()
# def auth_by_token(request, backend, token):
#     """Decorator that creates/authenticates a user with an access_token"""
#     user = request.backend.do_auth(
#         access_token=request.DATA.get('access_token')
#     )
#     if user:
#         return user
#     else:
#         return None


@api_view(['POST'])
def register_by_access_token(request, *args, **kwargs):
    # TODO: make me pretty, decorator? api_view
    # LD: looks fine :)
    social_serializer = SocialTokenSerializer(data=request.data)

    # LD: what on else?
    if social_serializer.is_valid():
        try:
            data = social_serializer.data
            strategy = load_strategy(request)
            backend = load_backend(strategy, data['backend'], None)
            user = backend.do_auth(data['social_token'])
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
                return _facebook_login_error()
        # TODO: this error contains some valueable information!
        except HTTPError:
            return _facebook_login_error()


@api_view(['POST'])
def login_by_access_token(request, *args, **kwargs):
    # TODO: make me pretty, decorator?
    social_serializer = SocialTokenSerializer(data=request.data)
    if social_serializer.is_valid():
        try:
            data = social_serializer.data
            strategy = load_strategy(request)
            backend = load_backend(strategy, data['backend'], None)
            user = backend.do_auth(data['social_token'])
            if user:
                login(request, user)
                returned_json = get_access_token(user)
                return JsonResponse(returned_json)
            else:
                return _facebook_login_error()
        except HTTPError:
            return _facebook_login_error()
