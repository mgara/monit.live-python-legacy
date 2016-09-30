
from ..lib.utils import get_value, json_list_append
from django.db import models


from pytz import timezone
from service import Service
from ..lib.metrics.system import MemoryCPUSystemMetrics


class System(Service):
    server = models.OneToOneField('Server')
    date_last = models.PositiveIntegerField(null=True)
    date = models.TextField(null=True)
    load_avg01_last = models.FloatField(null=True)
    load_avg05_last = models.FloatField(null=True)
    load_avg15_last = models.FloatField(null=True)
    cpu_user_last = models.FloatField(null=True)
    cpu_system_last = models.FloatField(null=True)
    cpu_wait_last = models.FloatField(null=True)
    memory_percent_last = models.FloatField(null=True)
    memory_kilobyte_last = models.PositiveIntegerField(null=True)
    swap_percent_last = models.FloatField(null=True)
    swap_kilobyte_last = models.PositiveIntegerField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        data_timestamp = int(get_value(service, "collected_sec", ""))

        system, created = cls.objects.get_or_create(server=server)
        system.service_type = get_value(service, "type", "")
        system.name = get_value(service, "", "", "name")
        system.status = get_value(service, "status", "")
        system.status_hint = get_value(service, "status_hint", "")
        system.monitor = get_value(service, "monitor", "")
        system.monitor_mode = get_value(service, "monitormode", "")
        system.pending_action = get_value(service, "pendingaction", "")
        tz = timezone(system.server.data_timezone)

        if get_value(service, "load", "avg01") != "none":
            system.date_last = data_timestamp
            system.date = json_list_append(system.date, system.date_last)
            system.load_avg01_last = float(get_value(service, "load", "avg01"))
            system.load_avg05_last = float(get_value(service, "load", "avg05"))
            system.load_avg15_last = float(get_value(service, "load", "avg15"))
            system.cpu_user_last = float(get_value(service, "cpu", "user"))
            system.cpu_system_last = float(get_value(service, "cpu", "system"))
            cpu_wait = get_value(service, "cpu", "wait")
            if cpu_wait != "none":
                system.cpu_wait_last = float(get_value(service, "cpu", "wait"))
            else:
                system.cpu_wait_last = float("0.0")
            system.memory_percent_last = float(
                get_value(service, "memory", "percent"))
            system.memory_kilobyte_last = int(
                get_value(service, "memory", "kilobyte"))
            system.swap_percent_last = float(
                get_value(service, "swap", "percent"))
            system.swap_kilobyte_last = int(
                get_value(service, "swap", "kilobyte"))
        system.save()

        if get_value(service, "load", "avg01") != "none":
            MemoryCPUSystemMetrics(system, server, data_timestamp)
        return system

    @classmethod
    def get_by_server(cls, server):
        system, created = cls.objects.get_or_create(server=server)
        return system
