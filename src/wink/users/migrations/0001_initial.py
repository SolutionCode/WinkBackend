# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import users.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('email', models.EmailField(unique=True, max_length=255, db_index=True)),
                ('phone_number', models.CharField(max_length=32, null=True, blank=True)),
                ('handle', models.CharField(db_index=True, unique=True, max_length=32, validators=[users.models.validate_handle])),
                ('display_name', models.CharField(max_length=64)),
                ('date_of_birth', models.DateField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=True, db_index=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
