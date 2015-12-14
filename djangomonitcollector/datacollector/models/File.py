from django.db import models

from service import Service
from utils import get_value, decode_status


class File(Service):
    server = models.ForeignKey('Server')

    @classmethod
    def update(cls, xmldoc, server, service):
        filename = get_value(service, "", "", "name")
        file, created = cls.objects.get_or_create(server=server, name=filename)
        file.name = filename
        file.status = decode_status(int(get_value(service, "status", "")))
        file.status_hint = get_value(service, "status_hint", "")
        file.monitor = get_value(service, "monitor", "")
        file.monitormode = get_value(service, "monitormode", "")
        file.pendingaction = get_value(service, "pendingaction", "")
        file.save()
