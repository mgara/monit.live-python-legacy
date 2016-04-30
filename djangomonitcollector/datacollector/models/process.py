import datetime
from django.db import models
from pytz import timezone

from service import Service
from ..lib.utils import get_value
from djangomonitcollector.datacollector.lib.elastic import publish_to_elasticsearch
from ..models import AggregationPeriod


class Process(Service):
    server = models.ForeignKey('Server')
    pid = models.IntegerField(null=True)
    ppid = models.IntegerField(null=True)
    uptime = models.PositiveIntegerField(null=True)
    children = models.PositiveIntegerField(null=True)
    cpu_percent_last = models.FloatField(null=True)
    memory_percent_last = models.FloatField(null=True)
    memory_kilobyte_last = models.PositiveIntegerField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        service_name = get_value(service, "", "", "name")
        process, created = cls.objects.get_or_create(server=server, name=service_name)
        process.service_type = get_value(service, "type", "")
        process.status = get_value(service, "status", "")
        process.status_hint = get_value(service, "status_hint", "")
        process.monitor = get_value(service, "monitor", "")
        process.monitor_mode = get_value(service, "monitormode", "")
        process.pending_action = get_value(service, "pendingaction", "")
        if get_value(service, "cpu", "percent") != "none":
            process.pid = get_value(service, "pid")
            process.ppid = get_value(service, "ppid")
            process.uptime = get_value(service, "uptime")
            process.children = get_value(service, "children")
            process.cpu_percent_last = float(get_value(service, "cpu", "percent"))
            process.memory_percent_last = float(get_value(service, "memory", "percent"))
            process.memory_kilobyte_last = int(get_value(service, "memory", "kilobyte"))
        process.save()
        if get_value(service, "cpu", "percent") != "none":
            colect_timestamp = int(get_value(service, "collected_sec", ""))
            entry = MemoryCPUProcessStats.create(
                    process,
                    process.server.data_timezone,
                    colect_timestamp,
                    process.cpu_percent_last,
                    process.memory_percent_last,
                    process.memory_kilobyte_last
            )
            MemoryCPUProcessStats.to_elasticsearch(
                entry,
                process.server.localhostname.replace('.','_'),
                process.name
                )
        return process

    @classmethod
    def get_by_name(cls, server, name):
        service, created = cls.objects.get_or_create(server=server, name=name)
        return service


class MemoryCPUProcessStats(models.Model):
    process_id = models.ForeignKey('Process')
    date_last = models.DateTimeField()
    cpu_percent = models.FloatField(null=True)
    memory_percent = models.FloatField(null=True)
    memory_kilobyte = models.PositiveIntegerField(null=True)

    @classmethod
    def create(
            cls,
            process,
            tz_str,
            unixtimestamp,
            cpu_percent,
            memory_percent,
            memory_kilobyte
    ):
        entry = cls()
        tz = timezone(tz_str)
        entry.date_last = datetime.datetime.fromtimestamp(unixtimestamp, tz)
        entry.process_id = process
        entry.cpu_percent = cpu_percent
        entry.memory_kilobyte = memory_kilobyte
        entry.memory_percent = memory_percent
        entry.save()
        return entry

    @classmethod
    def to_elasticsearch(cls, entry, server_name, processname):
        _doc = dict()
        _doc['timestamp'] = entry.date_last
        _doc['{}_process_{}_cpu_percent'.format(server_name, processname)] = entry.cpu_percent
        _doc['{}_process_{}_memory_percent'.format(server_name, processname)] = entry.memory_percent
        _doc['{}_process_{}_memory_kilobyte'.format(server_name, processname)] = entry.memory_kilobyte

        publish_to_elasticsearch(
            "monit",
            "process-stats",
            _doc
            )


class MemoryCPUProcessAggregatedStats(models.Model):
    process_id = models.ForeignKey('Process')
    date_last = models.DateTimeField()
    cpu_percent = models.FloatField(null=True)
    memory_percent = models.FloatField(null=True)
    memory_kilobyte = models.PositiveIntegerField(null=True)
    rule_id = models.ForeignKey(AggregationPeriod)

    @classmethod
    def create(
            cls,
            process,
            tz_str,
            unixtimestamp,
            cpu_percent,
            memory_percent,
            memory_kilobyte
    ):
        entry = cls()
        tz = timezone(tz_str)
        entry.date_last = datetime.datetime.fromtimestamp(unixtimestamp, tz)
        entry.process_id = process
        entry.cpu_percent = cpu_percent
        entry.memory_kilobyte = memory_kilobyte
        entry.memory_percent = memory_percent
        entry.save()
        return entry
