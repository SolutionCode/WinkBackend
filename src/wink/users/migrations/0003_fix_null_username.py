# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from users.models import User

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    #User = apps.get_model("users", "User")
    db_alias = schema_editor.connection.alias
    for user in User.objects.all():
        user.username = user.email
        user.save()
    print User.objects.all()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_handle_to_username'),
    ]

    operations = [
	    migrations.RunPython(
	            forwards_func,
	        ),
        migrations.AlterField(
            model_name='User',
            name='username',
            field=models.CharField(db_index=True, unique=True, max_length=255)
        ),
    ]
