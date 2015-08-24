# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
   dependencies = [
        ('users', '0001_initial'),
   ]
   operations = [
        migrations.AddField(
            model_name='User',
            name='username',
            field=models.CharField(db_index=True, null=True, blank=True, max_length=255)
        ),
        migrations.RemoveField(
            model_name='User',
            name='handle',
        ),
    ]
