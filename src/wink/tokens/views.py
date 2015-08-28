import base64
import json
import binascii
from urllib import unquote_plus

from braces.views import CsrfExemptMixin
from common.exceptions import WinkException
from common.renderers import JSONRenderer
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from oauth2_provider.models import Application
from requests import HTTPError
from rest_framework.views import APIView
from social.apps.django_app.utils import load_strategy, load_backend
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import login
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.views import TokenView, RevokeTokenView
from tokens.tools import get_access_token
from users.serializers import UserSerializer
from tokens.serializers import SocialTokenSerializer, EmptySerializer, OAuthTokenSerializer


class WinkTokenView(CsrfExemptMixin, View):
    BaseTokenView = None

    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):
        response = self.BaseTokenView.post(request, *args, **kwargs)
        return self._fix_error2errors_in_oauth(response)

    def _fix_error2errors_in_oauth(self, response):
        if response.content:
            d = json.loads(response.content)
            if 'error' in d:
                d = {'errors': [d['error']]}
            else:
                d = {'data': {OAuthTokenSerializer.resource_name: d}}
            response.content = json.dumps(d)
        return response


class WinkAcceptTokenView(WinkTokenView):
    BaseTokenView = TokenView()


class WinkRevokeTokenView(WinkTokenView):
    BaseTokenView = RevokeTokenView()


class SocialAccessTokenView(APIView):
    renderer_classes = (JSONRenderer,)
    app = None
    user = None

    def _get_client_id_and_secret(self, request):
        auth_string = request.META['HTTP_AUTHORIZATION'].split()[1]
        encoding = 'utf-8'
        try:
            b64_decoded = base64.b64decode(auth_string)
        except (TypeError, binascii.Error):
            raise WinkException("Failed basic auth: %s can't be decoded as base64")

        try:
            auth_string_decoded = b64_decoded.decode(encoding)
        except UnicodeDecodeError:
            raise WinkException("Failed basic auth: %s can't be decoded as unicode by %s" % auth_string,
                                encoding)

        client_id, client_secret = map(unquote_plus, auth_string_decoded.split(':', 1))
        return client_id, client_secret

    def post(self, request, format=None):
        social_serializer = SocialTokenSerializer(data=request.data)
        social_serializer.is_valid(raise_exception=True)
        client_id, client_secret = self._get_client_id_and_secret(request)
        try:
            self.app = Application.objects.get(client_id=client_id)
        except ObjectDoesNotExist:
            raise WinkException("client_id doesn't exist")
        try:
            data = social_serializer.data
            strategy = load_strategy(request)
            backend = load_backend(strategy, data['backend'], None)
            self.user = backend.do_auth(data['social_token'])
        except HTTPError as e:
            raise WinkException(e.message + " when connecting to " + data['backend'])

        if not self.user:
            raise WinkException("after token user is none")

        return None


class RegisterBySocialAccessTokenView(SocialAccessTokenView):
    serializer_class = EmptySerializer

    def post(self, request, format=None):
        response = super(RegisterBySocialAccessTokenView, self).post(request, format)
        if response:
            return response
        if not self.user.last_login:
            login(request, self.user)
            serializer = UserSerializer(self.user, context={'request': request})
            returned_json = {
                'user': serializer.data,
                'token': get_access_token(self.user, self.app)
            }
            return Response(returned_json)
        else:
            raise WinkException("user already registered")


class LoginBySocialAccessTokenView(SocialAccessTokenView):
    serializer_class = OAuthTokenSerializer

    def post(self, request, format=None):
        response = super(LoginBySocialAccessTokenView, self).post(request, format)
        if response:
            return response
        login(request, self.user)
        return Response(get_access_token(self.user, self.app))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def secret(request, *args, **kwargs):
    '''
    testing purpuse only
    :param request:
    :return:
    '''
    return JsonResponse({'status': 'success', 'user': request.user.pk})
