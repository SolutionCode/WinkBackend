from django.conf.urls import include, url

from users.views import UserRetrieveUpdateView, UserPublicRetrieveUpdateView


urlpatterns = [
    url(r'^(?P<pk>[0-9]+)$', UserRetrieveUpdateView.as_view(), name='user-detail'),
    url(r'^(?P<pk>[0-9]+)/public$', UserPublicRetrieveUpdateView.as_view(), name='user-detail-public'),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]