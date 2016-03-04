# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datacollector', '0002_auto_20160219_1322'),
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='datacollector.Service')),
                ('permission', models.CharField(max_length=4, null=True)),
                ('uid', models.IntegerField(null=True)),
                ('gid', models.IntegerField(null=True)),
                ('server', models.ForeignKey(to='datacollector.Server')),
            ],
            bases=('datacollector.service',),
        ),
    ]
