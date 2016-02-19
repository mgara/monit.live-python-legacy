# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationType',
            fields=[
                ('id', models.CharField(max_length=40, serialize=False, primary_key=True)),
                ('notification_service', models.CharField(max_length=255, null=True)),
                ('notification_type', models.CharField(max_length=255, null=True)),
                ('notification_state', models.CharField(max_length=255, null=True)),
                ('notification_action', models.CharField(max_length=255, null=True)),
                ('notification_message', models.CharField(max_length=255, null=True)),
                ('notification_class', models.CharField(max_length=32)),
                ('notification_label', models.CharField(max_length=100)),
                ('notification_enabled', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notification_plugin_extra_params', models.TextField(null=True)),
                ('notification_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
