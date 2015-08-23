from django.conf.urls import include, url

from users.views import UserCreateView, UserRetrieveView, secret


urlpatterns = [
    url(r'^(?P<pk>[0-9]+)$', UserRetrieveView.as_view(), name='user-detail'),
    url(r'^$', UserCreateView.as_view(), name='user-list'),
    url(r'^secret', secret, name='secret')
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]