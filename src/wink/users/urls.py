from django.conf.urls import include, url

from users.views import UserCreateView, UserRetrieveView


urlpatterns = [
    url(r'^users/(?P<pk>[0-9]+)', UserRetrieveView.as_view(), name='users-detail'),
    url(r'^users', UserCreateView.as_view(), name='users-list'),
]
