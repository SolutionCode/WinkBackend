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


def _facebook_login_error(message):
    return Response({"errors": [message]}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def register_by_access_token(request, *args, **kwargs):
    # TODO: make me pretty, decorator? api_view
    # LD: looks fine :)
    social_serializer = SocialTokenSerializer(data=request.data)
    # TODO: how DRF behaves on raise exception? it's handling exception correctly...
    social_serializer.is_valid(raise_exception=True)
    try:
        data = social_serializer.data
        strategy = load_strategy(request)
        backend = load_backend(strategy, data['backend'], None)
        user = backend.do_auth(data['social_token'])
        if user:
            if not user.last_login:
                login(request, user)
                returned_json = get_access_token(user, social_serializer.app)
                serializer = UserSerializer(user, context={'request': request})
                returned_json.update(serializer.data)
                return JsonResponse(returned_json)
            else:
                return Response({"errors": "user already registered"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return _facebook_login_error("after token user is none")
    except HTTPError as e:
        return _facebook_login_error(e.message + " when connecting to " + data['backend'])


@api_view(['POST'])
def login_by_access_token(request, *args, **kwargs):
    # TODO: make me pretty, decorator?
    social_serializer = SocialTokenSerializer(data=request.data)
    social_serializer.is_valid(raise_exception=True)
    try:
        data = social_serializer.data
        strategy = load_strategy(request)
        backend = load_backend(strategy, data['backend'], None)
        user = backend.do_auth(data['social_token'])
        if user:
            login(request, user)
            returned_json = get_access_token(user, social_serializer.app)
            return JsonResponse(returned_json)
        else:
            return _facebook_login_error("after token user is none")
    except HTTPError as e:
        return _facebook_login_error(e.message + " when connecting to " + data['backend'])
