import base64
import json
import binascii
from urllib import unquote_plus

from django.core.exceptions import ObjectDoesNotExist
from oauth2_provider.models import Application
from requests import HTTPError
from social.apps.django_app.utils import load_strategy, load_backend
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import login
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.views import TokenView, RevokeTokenView
from tokens.tools import get_access_token
from users.serializers import UserSerializer
from tokens.serializers import SocialTokenSerializer


def fix_error2errors_in_oauth(response):
    d = json.loads(response.content)
    if 'error' in d:
        d = {'errors': [d['error']]}
    response.content = json.dumps(d)
    return response


class WinkTokenView(TokenView):
    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):
        '''
        extended OAuth token view, because error should be changed to errors
        '''
        response = super(WinkTokenView, self).post(request, *args, **kwargs)
        return fix_error2errors_in_oauth(response)


class WinkRevokeTokenView(RevokeTokenView):
    """
    Implements an endpoint to revoke access or refresh tokens
    """

    def post(self, request, *args, **kwargs):
        response = super(WinkRevokeTokenView, self).post(request, *args, **kwargs)
        return fix_error2errors_in_oauth(response)


def _facebook_login_error(message):
    return Response({"errors": [message]}, status=status.HTTP_401_UNAUTHORIZED)


def _get_client_id_and_secret(request):
    auth_string = request.META['HTTP_AUTHORIZATION'].split()[1]
    encoding = 'utf-8'
    try:
        b64_decoded = base64.b64decode(auth_string)
    except (TypeError, binascii.Error):
        print ("Failed basic auth: %s can't be decoded as base64", auth_string)
        return False

    try:
        auth_string_decoded = b64_decoded.decode(encoding)
    except UnicodeDecodeError:
        print ("Failed basic auth: %s can't be decoded as unicode by %s",
               auth_string,
               encoding)
        return False

    client_id, client_secret = map(unquote_plus, auth_string_decoded.split(':', 1))
    return client_id, client_secret


@api_view(['POST'])
def register_by_access_token(request, *args, **kwargs):
    # TODO: make me pretty, decorator? api_view
    # LD: looks fine :)
    # print request.META
    social_serializer = SocialTokenSerializer(data=request.data)
    social_serializer.is_valid(raise_exception=True)
    try:
        # TODO: this is really bad!
        client_id, client_secret = _get_client_id_and_secret(request)
        try:
            app = Application.objects.get(client_id=client_id)
        except ObjectDoesNotExist:
            return Response({"errors": ["client_id doesn't exist"]}, status=status.HTTP_400_BAD_REQUEST)
        data = social_serializer.data
        strategy = load_strategy(request)
        backend = load_backend(strategy, data['backend'], None)
        user = backend.do_auth(data['social_token'])
        if user:
            if not user.last_login:
                login(request, user)
                serializer = UserSerializer(user, context={'request': request})
                returned_json = {
                    'user': serializer.data,
                    'token': get_access_token(user, app)
                }
                return JsonResponse({'data': returned_json})
            else:
                return Response({"errors": ["user already registered"]}, status=status.HTTP_400_BAD_REQUEST)
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
        # TODO: this is really bad!
        client_id, client_secret = _get_client_id_and_secret(request)
        try:
            app = Application.objects.get(client_id=client_id)
        except ObjectDoesNotExist:
            return Response({"errors": ["client_id doesn't exist"]}, status=status.HTTP_400_BAD_REQUEST)
        data = social_serializer.data
        strategy = load_strategy(request)
        backend = load_backend(strategy, data['backend'], None)
        user = backend.do_auth(data['social_token'])
        if user:
            login(request, user)
            returned_json = {
                'token': get_access_token(user, app)
            }
            return JsonResponse({'data': returned_json})
        else:
            return _facebook_login_error("after token user is none")
    except HTTPError as e:
        return _facebook_login_error(e.message + " when connecting to " + data['backend'])


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def secret(request, *args, **kwargs):
    '''
    testing purpuse only
    :param request:
    :return:
    '''
    return JsonResponse({'status': 'success', 'user': request.user.pk})
