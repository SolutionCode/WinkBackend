from django.conf.urls import include, url

from users.views import UserCreateView, UserRetrieveView, register_by_access_token


urlpatterns = [
    url(r'^(?P<pk>[0-9]+)$', UserRetrieveView.as_view(), name='user-detail'),
    url(r'^$', UserCreateView.as_view(), name='user-list'),
    url(r'^register-by-token/(?P<backend>[^/]+)/$', register_by_access_token),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]