from django.conf.urls import url, include

from tokens import views
from views import register_by_access_token, login_by_access_token, secret

urlpatterns = [
    url(r'^oauth2/token/$', views.WinkTokenView.as_view(), name="token"),
    url(r'^oauth2/revoke_token/$', views.RevokeTokenView.as_view(), name="token"),
    url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^social/register/$', register_by_access_token, name='social-register'),
    url(r'^social/login/$', login_by_access_token, name='social-login'),
]


urlpatterns += [
    url(r'^secret', secret, name='secret')
]