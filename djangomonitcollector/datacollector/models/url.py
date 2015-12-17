from django.db import models

from service import Service
from utils import get_value


class Host(Service):
    server = models.ForeignKey('Server')

    @classmethod
    def update(cls, xmldoc, server, service):
        hostname = get_value(service, "", "", "name")
        host, created = cls.objects.get_or_create(server=server, name=hostname)
        host.name = hostname
        host.service_type = get_value(service, "type", "")
        host.status = get_value(service, "status", "")
        host.status_hint = get_value(service, "status_hint", "")
        host.monitor = get_value(service, "monitor", "")
        host.monitormode = get_value(service, "monitormode", "")
        host.pendingaction = get_value(service, "pendingaction", "")
        host.save()
