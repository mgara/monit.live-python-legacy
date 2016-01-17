import time

from django.db import models

from service import Service
from utils import get_value, json_list_append
from pytz import timezone
import datetime


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
        system, created = cls.objects.get_or_create(server=server)
        system.service_type = get_value(service, "type", "")
        system.name = get_value(service, "", "", "name")
        system.status = get_value(service, "status", "")
        system.status_hint = get_value(service, "status_hint", "")
        system.monitor = get_value(service, "monitor", "")
        system.monitor_mode = get_value(service, "monitormode", "")
        system.pending_action = get_value(service, "pendingaction", "")
        if get_value(service, "load", "avg01") != "none":
            system.date_last = int(time.time())
            system.date = json_list_append(system.date, system.date_last)
            system.load_avg01_last = float(get_value(service, "load", "avg01"))
            system.load_avg05_last = float(get_value(service, "load", "avg05"))
            system.load_avg15_last = float(get_value(service, "load", "avg15"))
            system.cpu_user_last = float(get_value(service, "cpu", "user"))
            system.cpu_system_last = float(get_value(service, "cpu", "system"))
            system.cpu_wait_last = float(get_value(service, "cpu", "wait"))
            system.memory_percent_last = float(get_value(service, "memory", "percent"))
            system.memory_kilobyte_last = int(get_value(service, "memory", "kilobyte"))
            system.swap_percent_last = float(get_value(service, "swap", "percent"))
            system.swap_kilobyte_last = int(get_value(service, "swap", "kilobyte"))
        system.save()
        if get_value(service, "load", "avg01") != "none":
            colect_timestamp = int(get_value(service, "collected_sec", ""))
            MemoryCPUSystemStats.create(
                system,
                system.server.data_timezone,
                colect_timestamp,
                system.load_avg01_last,
                system.load_avg05_last,
                system.load_avg15_last,
                system.cpu_user_last,
                system.cpu_system_last,
                system.cpu_wait_last,
                system.memory_percent_last,
                system.memory_kilobyte_last,
                system.swap_percent_last,
                system.swap_kilobyte_last
            )
        return system

    @classmethod
    def get_system_service(cls,server):
        system, created = cls.objects.get_or_create(server=server)
        return system

class MemoryCPUSystemStats(models.Model):
    system_id = models.ForeignKey('System')
    date_last = models.DateTimeField()
    load_avg01 = models.FloatField(null=True)
    load_avg05 = models.FloatField(null=True)
    load_avg15 = models.FloatField(null=True)
    cpu_user = models.FloatField(null=True)
    cpu_system = models.FloatField(null=True)
    cpu_wait = models.FloatField(null=True)
    memory_percent = models.FloatField(null=True)
    memory_kilobyte = models.PositiveIntegerField(null=True)
    swap_percent = models.FloatField(null=True)
    swap_kilobyte = models.PositiveIntegerField(null=True)

    @classmethod
    def create(cls,
               system,
               tz_str,
               unixtimestamp,
               load_avg01,
               load_avg05,
               load_avg15,
               cpu_user,
               cpu_system,
               cpu_wait,
               memory_percent,
               memory_kilobyte,
               swap_percent,
               swap_kilobyte
               ):
        entry = cls(system_id=system)
        tz = timezone(tz_str)
        entry.date_last= datetime.datetime.fromtimestamp(unixtimestamp).replace(tzinfo=tz)
        entry.load_avg01 = load_avg01
        entry.load_avg05 = load_avg05
        entry.load_avg15 = load_avg15
        entry.cpu_user = cpu_user
        entry.cpu_system = cpu_system
        entry.cpu_wait = cpu_wait
        entry.memory_percent = memory_percent
        entry.memory_kilobyte = memory_kilobyte
        entry.swap_percent = swap_percent
        entry.swap_kilobyte = swap_kilobyte
        entry.save()
        return entry
