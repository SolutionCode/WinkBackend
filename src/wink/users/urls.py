from django.conf.urls import include, url

from users.api import UserResource


urlpatterns = [
    url(r'^users/', include(UserResource.urls())),
]
