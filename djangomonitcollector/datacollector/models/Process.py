import time

from django.db import models

from utils import get_value, decode_status, json_list_append
from service import Service


# we call everything else a Process, not only type=3
class Process(Service):
    server = models.ForeignKey('Server')
    date_last = models.PositiveIntegerField(null=True)
    date = models.TextField(null=True)
    pid = models.IntegerField(null=True)
    ppid = models.IntegerField(null=True)
    uptime = models.PositiveIntegerField(null=True)
    children = models.PositiveIntegerField(null=True)
    cpu_percenttotal_last = models.FloatField(null=True)
    cpu_percenttotal = models.TextField(null=True)
    memory_percenttotal_last = models.FloatField(null=True)
    memory_percenttotal = models.TextField(null=True)
    memory_kilobytetotal_last = models.PositiveIntegerField(null=True)
    memory_kilobytetotal = models.TextField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        service_name = get_value(service, "", "", "name")
        process, created = cls.objects.get_or_create(server=server, name=service_name)
        process.status = decode_status(int(get_value(service, "status", "")))
        process.status_hint = get_value(service, "status_hint", "")
        process.monitor = get_value(service, "monitor", "")
        process.monitormode = get_value(service, "monitormode", "")
        process.pendingaction = get_value(service, "pendingaction", "")
        if get_value(service, "cpu", "percent") != "none":
            process.pid = get_value(service, "pid")
            process.ppid = get_value(service, "ppid")
            process.uptime = get_value(service, "uptime")
            process.children = get_value(service, "children")

            process.date_last = int(time.time())
            process.date = json_list_append(process.date, process.date_last)
            process.cpu_percenttotal_last = float(get_value(service, "cpu", "percenttotal"))
            process.cpu_percenttotal = json_list_append(process.cpu_percenttotal, process.cpu_percenttotal_last)
            process.memory_percenttotal_last = float(get_value(service, "memory", "percenttotal"))
            process.memory_percenttotal = json_list_append(process.memory_percenttotal,
                                                           process.memory_percenttotal_last)
            process.memory_kilobytetotal_last = int(get_value(service, "memory", "kilobytetotal"))
            process.memory_kilobytetotal = json_list_append(process.memory_kilobytetotal,
                                                            process.memory_kilobytetotal_last)
        process.save()
