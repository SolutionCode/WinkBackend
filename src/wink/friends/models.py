from django.db import models
from django.conf import settings


class Friend(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " friends with " + self.friend.username

