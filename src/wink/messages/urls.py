from django.conf.urls import url

from messages import views

urlpatterns = [
    url(r'^$', views.PostMessage.as_view()),
    url(r'^(?P<id>[0-9]+)$', views.GetMessageHistory.as_view())
]