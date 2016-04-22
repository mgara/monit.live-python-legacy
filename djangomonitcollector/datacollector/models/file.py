from django.db import models

from service import Service
from ..lib.utils import get_value, get_int


class File(Service):
    server = models.ForeignKey('Server')
    size = models.PositiveIntegerField(null=True)
    permission = models.CharField(null=True, max_length=4)
    uid = models.IntegerField(null=True)
    gid = models.IntegerField(null=True)
    timestamp = models.CharField(null=True, max_length=20)

    @classmethod
    def update(cls, xmldoc, server, service):
        filename = get_value(service, "", "", "name")
        file_, created = cls.objects.get_or_create(server=server, name=filename)
        file_.name = filename
        file_.status = get_value(service, "status", "")
        file_.status_hint = get_value(service, "status_hint", "")
        file_.monitor = get_value(service, "monitor", "")
        file_.service_type = get_value(service, "type", "")
        file_.monitor_mode = get_value(service, "monitormode", "")
        file_.pending_action = get_value(service, "pendingaction", "")
        file_.s_id = file_.server.id

        file_.size = get_int(service, "size", "")
        file_.permission = get_value(service, "mode", "")
        file_.uid = get_int(service, "uid", "")
        file_.gid = get_int(service, "gid", "")
        file_.timestamp = get_value(service, "timestamp", "")

        file_.save()
        return file_

    @classmethod
    def get_by_name(cls, server, name):
        service, created = cls.objects.get_or_create(server=server, name=name)
        return service
