# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacollector', '0003_directory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='http_password',
            field=models.CharField(default=b'admin', max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='http_username',
            field=models.CharField(default=b'monit', max_length=45, null=True),
        ),
    ]
