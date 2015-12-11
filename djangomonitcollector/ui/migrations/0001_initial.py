# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(null=True)),
                ('release', models.TextField(null=True)),
                ('version', models.TextField(null=True)),
                ('machine', models.TextField(null=True)),
                ('cpu', models.IntegerField(null=True)),
                ('memory', models.IntegerField(null=True)),
                ('swap', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('monit_id', models.CharField(unique=True, max_length=32)),
                ('monit_version', models.TextField(null=True)),
                ('localhostname', models.TextField(null=True)),
                ('uptime', models.IntegerField(null=True)),
                ('address', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('status', models.TextField(null=True)),
                ('status_hint', models.IntegerField(null=True)),
                ('monitor', models.IntegerField(null=True)),
                ('monitormode', models.IntegerField(null=True)),
                ('pendingaction', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FileSystem',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='datacollector.Service')),
                ('file_system', models.TextField(null=True)),
                ('mode', models.TextField(null=True)),
                ('flags', models.IntegerField(null=True)),
                ('blocks_percent', models.FloatField(null=True)),
                ('blocks_percent_last', models.FloatField(null=True)),
                ('blocks_usage', models.FloatField(null=True)),
                ('blocks_usage_last', models.FloatField(null=True)),
                ('blocks_total', models.FloatField(null=True)),
                ('inode_percent', models.FloatField(null=True)),
                ('inode_percent_last', models.FloatField(null=True)),
                ('inode_usage', models.IntegerField(null=True)),
                ('inode_usage_last', models.IntegerField(null=True)),
                ('inode_total', models.IntegerField(null=True)),
                ('server', models.ForeignKey(to='datacollector.Server')),
            ],
            bases=('datacollector.service',),
        ),
        migrations.CreateModel(
            name='Net',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='datacollector.Service')),
                ('server', models.ForeignKey(to='datacollector.Server')),
            ],
            bases=('datacollector.service',),
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='datacollector.Service')),
                ('date_last', models.PositiveIntegerField(null=True)),
                ('date', models.TextField(null=True)),
                ('pid', models.IntegerField(null=True)),
                ('ppid', models.IntegerField(null=True)),
                ('uptime', models.PositiveIntegerField(null=True)),
                ('children', models.PositiveIntegerField(null=True)),
                ('cpu_percenttotal_last', models.FloatField(null=True)),
                ('cpu_percenttotal', models.TextField(null=True)),
                ('memory_percenttotal_last', models.FloatField(null=True)),
                ('memory_percenttotal', models.TextField(null=True)),
                ('memory_kilobytetotal_last', models.PositiveIntegerField(null=True)),
                ('memory_kilobytetotal', models.TextField(null=True)),
                ('server', models.ForeignKey(to='datacollector.Server')),
            ],
            bases=('datacollector.service',),
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='datacollector.Service')),
                ('date_last', models.PositiveIntegerField(null=True)),
                ('date', models.TextField(null=True)),
                ('load_avg01_last', models.FloatField(null=True)),
                ('load_avg01', models.TextField(null=True)),
                ('load_avg05_last', models.FloatField(null=True)),
                ('load_avg05', models.TextField(null=True)),
                ('load_avg15_last', models.FloatField(null=True)),
                ('load_avg15', models.TextField(null=True)),
                ('cpu_user_last', models.FloatField(null=True)),
                ('cpu_user', models.TextField(null=True)),
                ('cpu_system_last', models.FloatField(null=True)),
                ('cpu_system', models.TextField(null=True)),
                ('cpu_wait_last', models.FloatField(null=True)),
                ('cpu_wait', models.TextField(null=True)),
                ('memory_percent_last', models.FloatField(null=True)),
                ('memory_percent', models.TextField(null=True)),
                ('memory_kilobyte_last', models.PositiveIntegerField(null=True)),
                ('memory_kilobyte', models.TextField(null=True)),
                ('swap_percent_last', models.FloatField(null=True)),
                ('swap_percent', models.TextField(null=True)),
                ('swap_kilobyte_last', models.PositiveIntegerField(null=True)),
                ('swap_kilobyte', models.TextField(null=True)),
                ('server', models.OneToOneField(to='datacollector.Server')),
            ],
            bases=('datacollector.service',),
        ),
        migrations.AddField(
            model_name='platform',
            name='server',
            field=models.OneToOneField(to='datacollector.Server'),
        ),
    ]
