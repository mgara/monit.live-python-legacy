from django.db import models

from utils import decode_status, get_value, get_int, get_string
from service import Service


class Program(Service):
    server = models.ForeignKey('Server')
    date_last = models.PositiveIntegerField(null=True)
    date = models.TextField(null=True)
    started = models.IntegerField(null=True)
    output = models.TextField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        service_name = get_value(service, "", "", "name")
        program, created = cls.objects.get_or_create(server=server, name=service_name)
        program.status = decode_status(int(get_value(service, "status", "")))
        program.status_hint = get_value(service, "status_hint", "")
        program.monitor = get_value(service, "monitor", "")
        program.monitormode = get_value(service, "monitormode", "")
        program.pendingaction = get_value(service, "pendingaction", "")
        program.started = get_int(service, "program.started", -1)
        program.output = get_string(service, "program.output", "")
        program.save()
