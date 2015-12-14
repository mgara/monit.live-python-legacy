from django.db import models

from service import Service
from utils import decode_status, get_value


class URL(Service):
    server = models.ForeignKey('Server')

    @classmethod
    def update(cls, xmldoc, server, service):
        url_str = get_value(service, "", "", "name")
        url, created = cls.objects.get_or_create(server=server, name=url_str)
        url.name = url_str
        url.status = decode_status(int(get_value(service, "status", "")))
        url.status_hint = get_value(service, "status_hint", "")
        url.monitor = get_value(service, "monitor", "")
        url.monitormode = get_value(service, "monitormode", "")
        url.pendingaction = get_value(service, "pendingaction", "")
        url.save()
