from django.conf.urls import include, url

from users.views import UserCreateView, UserRetrieveView, register_by_access_token, login_by_access_token, secret


urlpatterns = [
    url(r'^(?P<pk>[0-9]+)$', UserRetrieveView.as_view(), name='user-detail'),
    url(r'^$', UserCreateView.as_view(), name='user-list'),
    url(r'^register-social/(?P<backend>[^/]+)/(?P<token>[a-zA-Z0-9]+)/$', register_by_access_token),
    url(r'^login-social/(?P<backend>[^/]+)/(?P<token>[a-zA-Z0-9]+)/$', login_by_access_token),
    url(r'^secret', secret)
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]