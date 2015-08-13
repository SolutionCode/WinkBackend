from django.db import models
from django.conf import settings
# Create your models here.

class Friend(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user')
    friend_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_id.username + " friends with " + self.friend_id.username


