from django.conf.urls import include, url

from users.views import user_detail, users_list


urlpatterns = [
    url(r'^users/(?P<pk>[0-9]+)', user_detail, name='users-detail'),
    url(r'^users', users_list, name='users-list'),
]
