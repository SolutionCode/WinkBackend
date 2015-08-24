from django.conf.urls import include, url

from users.views import UserRetrieveUpdateView


urlpatterns = [
    url(r'^(?P<pk>[0-9]+)$', UserRetrieveUpdateView.as_view(), name='user-detail'),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]