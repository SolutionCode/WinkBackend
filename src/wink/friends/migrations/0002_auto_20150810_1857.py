# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('friends', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='friend_id',
            field=models.ForeignKey(related_name='friend_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='friend',
            name='user_id',
            field=models.ForeignKey(related_name='user_id', to=settings.AUTH_USER_MODEL),
        ),
    ]
