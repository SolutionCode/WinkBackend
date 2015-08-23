from django.conf.urls import url
from tokens import views

urlpatterns = [
    url(r'^token/$', views.WinkTokenView.as_view(), name="token"),
]
