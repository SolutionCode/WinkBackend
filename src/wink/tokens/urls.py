from django.conf.urls import url
from django.conf import settings

from tokens import views
from views import register_by_access_token, login_by_access_token, secret

urlpatterns = [
    url(r'^oauth2/token/$', views.WinkTokenView.as_view(), name="token"),
    url(r'^social/register/$', register_by_access_token, name='social-register'),
    url(r'^social/login/$', login_by_access_token, name='social-login'),
]


urlpatterns += [
    url(r'^secret', secret, name='secret')
]