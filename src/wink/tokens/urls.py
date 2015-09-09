from django.conf.urls import url, include
from oauth2_provider.views import ApplicationList

from views import RegisterBySocialAccessTokenView, secret, LoginBySocialAccessTokenView, WinkAcceptTokenView, \
    WinkRevokeTokenView

urlpatterns = [
    url(r'^oauth2/token/$', WinkAcceptTokenView.as_view(), name="token"),
    url(r'^oauth2/revoke_token/$', WinkRevokeTokenView.as_view(), name="revoke-token"),
    url(r'^oauth2/applications/$', ApplicationList.as_view(), name="register-app"),
    url(r'^social/register/$', RegisterBySocialAccessTokenView.as_view(), name='social-register'),
    url(r'^social/login/$', LoginBySocialAccessTokenView.as_view(), name='social-login'),
]

urlpatterns += [
    url(r'^secret', secret, name='secret')
]
