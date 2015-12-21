from django.db import models

from service import Service
from utils import get_value


class File(Service):
    server = models.ForeignKey('Server')

    @classmethod
    def update(cls, xmldoc, server, service):
        filename = get_value(service, "", "", "name")
        file_, created = cls.objects.get_or_create(server=server, name=filename)
        file_.name = filename
        file_.status = get_value(service, "status", "")
        file_.status_hint = get_value(service, "status_hint", "")
        file_.monitor = get_value(service, "monitor", "")
        file_.monitormode = get_value(service, "monitormode", "")
        file_.pendingaction = get_value(service, "pendingaction", "")
        file_.s_id = file_.server.id
        file_.save()
        return file