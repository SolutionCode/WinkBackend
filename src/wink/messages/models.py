from django.db import models
from django.conf import settings


class Message(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='from_user')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='to_user')
    body = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return "Message from " + self.from_user.username + " to " + self.to_user.username
