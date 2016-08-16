
from django.db import models

from service import Service
from ..lib.utils import get_value, get_float
from ..lib.metrics.fs import FsAndDiskUsageMetrics


class FileSystem(Service):
    server = models.ForeignKey('Server')
    display_name = models.TextField(null=True)
    date_last = models.PositiveIntegerField(null=True)
    file_system = models.TextField(null=True)
    mode = models.TextField(null=True)
    flags = models.IntegerField(null=True)
    blocks_total = models.FloatField(null=True)
    inode_total = models.FloatField(null=True)
    blocks_percent_last = models.FloatField(null=True)
    blocks_usage_last = models.FloatField(null=True)
    inode_percent_last = models.FloatField(null=True)
    inode_usage_last = models.FloatField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        fs_name = get_value(service, "", "", "name")
        filesystem, created = cls.objects.get_or_create(
            server=server, name=fs_name)
        filesystem.service_type = get_value(service, "type", "")
        filesystem.name = fs_name
        filesystem.display_name = fs_name.replace("___", "__").replace(
            "__", "_").replace("_", "/").replace("//", "/")
        filesystem.status = get_value(service, "status", "")
        filesystem.status_hint = get_value(service, "status_hint", "")
        filesystem.monitor = get_value(service, "monitor", "")
        filesystem.monitor_mode = get_value(service, "monitormode", "")
        filesystem.pending_action = get_value(service, "pendingaction", "")
        percent_last = get_float(service, "block.percent")
        if percent_last:
            filesystem.blocks_percent_last = percent_last
            filesystem.inode_percent_last = get_float(service, "inode.percent")
            filesystem.blocks_usage_last = get_float(service, "block.usage")
            filesystem.inode_usage_last = get_float(service, "inode.usage")
            filesystem.blocks_total = get_float(service, "block.total")
            filesystem.inode_total = get_float(service, "inode.total")

        filesystem.save()

        if percent_last:
            colect_timestamp = int(get_value(service, "collected_sec", ""))
            FsAndDiskUsageMetrics(filesystem, server, colect_timestamp)
        return filesystem

    @classmethod
    def get_by_name(cls, server, name):
        service, created = cls.objects.get_or_create(server=server, name=name)
        return service
