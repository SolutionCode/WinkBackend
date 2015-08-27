from django.conf.urls import url, include

from tokens import views
from views import RegisterBySocialAccessTokenView, secret, LoginBySocialAccessTokenView

urlpatterns = [
    url(r'^oauth2/token/$', views.WinkTokenView.as_view(), name="token"),
    url(r'^oauth2/revoke_token/$', views.RevokeTokenView.as_view(), name="revoke-token"),
    url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^social/register/$', RegisterBySocialAccessTokenView.as_view(), name='social-register'),
    url(r'^social/login/$', LoginBySocialAccessTokenView.as_view(), name='social-login'),
]

urlpatterns += [
    url(r'^secret', secret, name='secret')
]
