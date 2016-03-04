from django.db import models

from service import Service
from utils import get_value, get_int


class Directory(Service):
    server = models.ForeignKey('Server')
    permission = models.CharField(null=True, max_length=4)
    uid = models.IntegerField(null=True)
    gid = models.IntegerField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        directory_name = get_value(service, "", "", "name")
        directory, created = cls.objects.get_or_create(server=server, name=directory_name)
        directory.name = directory_name
        directory.status = get_value(service, "status", "")
        directory.status_hint = get_value(service, "status_hint", "")
        directory.monitor = get_value(service, "monitor", "")
        directory.service_type = get_value(service, "type", "")
        directory.monitor_mode = get_value(service, "monitormode", "")
        directory.pending_action = get_value(service, "pendingaction", "")
        directory.s_id = directory.server.id

        directory.permission = get_value(service, "mode", "")
        directory.uid = get_int(service, "uid", "")
        directory.gid = get_int(service, "gid", "")

        directory.save()
        return directory

    @classmethod
    def get_by_name(cls, server, name):
        service, created = cls.objects.get_or_create(server=server, name=name)
        return service
