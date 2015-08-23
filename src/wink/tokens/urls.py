from django.conf.urls import url
from tokens import views
from views import register_by_access_token, login_by_access_token

urlpatterns = [
    url(r'^oauth2/token/$', views.WinkTokenView.as_view(), name="token"),
    url(r'^register-social/(?P<backend>[^/]+)/(?P<token>[a-zA-Z0-9]+)/$', register_by_access_token, name='register-social'),
    url(r'^login-social/(?P<backend>[^/]+)/(?P<token>[a-zA-Z0-9]+)/$', login_by_access_token, name='login-social'),
]
