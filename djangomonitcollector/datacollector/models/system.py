import time

from django.db import models

from service import Service
from utils import decode_status, get_value, json_list_append



# Service type=5
class System(Service):
    server = models.OneToOneField('Server')
    date_last = models.PositiveIntegerField(null=True)
    date = models.TextField(null=True)
    load_avg01_last = models.FloatField(null=True)
    load_avg01 = models.TextField(null=True)
    load_avg05_last = models.FloatField(null=True)
    load_avg05 = models.TextField(null=True)
    load_avg15_last = models.FloatField(null=True)
    load_avg15 = models.TextField(null=True)
    cpu_user_last = models.FloatField(null=True)
    cpu_user = models.TextField(null=True)
    cpu_system_last = models.FloatField(null=True)
    cpu_system = models.TextField(null=True)
    cpu_wait_last = models.FloatField(null=True)
    cpu_wait = models.TextField(null=True)
    memory_percent_last = models.FloatField(null=True)
    memory_percent = models.TextField(null=True)
    memory_kilobyte_last = models.PositiveIntegerField(null=True)
    memory_kilobyte = models.TextField(null=True)
    swap_percent_last = models.FloatField(null=True)
    swap_percent = models.TextField(null=True)
    swap_kilobyte_last = models.PositiveIntegerField(null=True)
    swap_kilobyte = models.TextField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        system, created = cls.objects.get_or_create(server=server)
        system.name = get_value(service, "", "", "name")
        system.status = decode_status(int(get_value(service, "status", "")))
        system.status_hint = get_value(service, "status_hint", "")
        system.monitor = get_value(service, "monitor", "")
        system.monitormode = get_value(service, "monitormode", "")
        system.pendingaction = get_value(service, "pendingaction", "")
        if get_value(service, "load", "avg01") != "none":
            system.date_last = int(time.time())
            system.date = json_list_append(system.date, system.date_last)

            system.load_avg01_last = float(get_value(service, "load", "avg01"))
            system.load_avg01 = json_list_append(system.load_avg01, system.load_avg01_last)
            system.load_avg05_last = float(get_value(service, "load", "avg05"))
            system.load_avg05 = json_list_append(system.load_avg05, system.load_avg05_last)
            system.load_avg15_last = float(get_value(service, "load", "avg15"))
            system.load_avg15 = json_list_append(system.load_avg15, system.load_avg15_last)

            system.cpu_user_last = float(get_value(service, "cpu", "user"))
            system.cpu_user = json_list_append(system.cpu_user, system.cpu_user_last)
            system.cpu_system_last = float(get_value(service, "cpu", "system"))
            system.cpu_system = json_list_append(system.cpu_system, system.cpu_system_last)
            system.cpu_wait_last = float(get_value(service, "cpu", "wait"))
            system.cpu_wait = json_list_append(system.cpu_wait, system.cpu_wait_last)

            system.memory_percent_last = float(get_value(service, "memory", "percent"))
            system.memory_percent = json_list_append(system.memory_percent, system.memory_percent_last)
            system.memory_kilobyte_last = int(get_value(service, "memory", "kilobyte"))
            system.memory_kilobyte = json_list_append(system.memory_kilobyte, system.memory_kilobyte_last)

            system.swap_percent_last = float(get_value(service, "swap", "percent"))
            system.swap_percent = json_list_append(system.swap_percent, system.swap_percent_last)
            system.swap_kilobyte_last = int(get_value(service, "swap", "kilobyte"))
            system.swap_kilobyte = json_list_append(system.swap_kilobyte, system.swap_kilobyte_last)
        system.save()
