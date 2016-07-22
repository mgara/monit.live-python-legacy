from django.db import models

from service import Service
from ..lib.utils import get_value
from ..lib.metrics.process import MemoryCPUProcessMetrics


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
            MemoryCPUProcessMetrics(process, server, colect_timestamp )
        return process

    @classmethod
    def get_by_name(cls, server, name):
        service, created = cls.objects.get_or_create(server=server, name=name)
        return service



