from django.db import models

from service import Service
from ..lib.utils import get_value, get_int, get_string


class Program(Service):
    server = models.ForeignKey('Server')
    date_last = models.PositiveIntegerField(null=True)
    date = models.TextField(null=True)
    started = models.IntegerField(null=True)
    output = models.TextField(null=True)
    exitcode = models.CharField(null=True, max_length=5)

    @classmethod
    def update(cls, xmldoc, server, service):
        service_name = get_value(service, "", "", "name")
        program, created = cls.objects.get_or_create(server=server, name=service_name)
        program.status = get_value(service, "status", "")
        program.service_type = get_value(service, "type", "")
        program.status_hint = get_value(service, "status_hint", "")
        program.monitor = get_value(service, "monitor", "")
        program.monitor_mode = get_value(service, "monitormode", "")
        program.pending_action = get_value(service, "pendingaction", "")
        program.started = get_int(service, "program.started", -1)
        program.output = get_string(service, "program.output", "")
        program.exitcode = get_string(service, "program.status", "")
        program.save()
        return program

    @classmethod
    def get_by_name(cls, server, name):
        service, created = cls.objects.get_or_create(server=server, name=name)
        return service
