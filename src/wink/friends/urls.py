from django.conf.urls import include, url

from friends import views

urlpatterns = [
    url(r'^$', views.Friends.as_view()),
    url(r'^/login$', views.login_user)
]