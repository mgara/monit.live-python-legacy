from django.db import models

from service import Service
from utils import get_value, decode_status, json_list_append


class FileSystem(Service):
    server = models.ForeignKey('Server')
    date_last = models.PositiveIntegerField(null=True)
    file_system = models.TextField(null=True)
    mode = models.TextField(null=True)
    flags = models.IntegerField(null=True)

    blocks_percent = models.TextField(null=True)
    blocks_percent_last = models.FloatField(null=True)
    blocks_usage = models.TextField(null=True)
    blocks_usage_last = models.FloatField(null=True)
    blocks_total = models.TextField(null=True)

    inode_percent = models.TextField(null=True)
    inode_percent_last = models.FloatField(null=True)
    inode_usage = models.TextField(null=True)
    inode_usage_last = models.IntegerField(null=True)
    inode_total = models.TextField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        fs_name = get_value(service, "", "", "name")
        fs_name.replace('_', '')
        filesystem, created = cls.objects.get_or_create(server=server, name=fs_name)
        filesystem.name = fs_name
        filesystem.status = decode_status(int(get_value(service, "status", "")))
        filesystem.status_hint = get_value(service, "status_hint", "")
        filesystem.monitor = get_value(service, "monitor", "")
        filesystem.monitormode = get_value(service, "monitormode", "")
        filesystem.pendingaction = get_value(service, "pendingaction", "")

        # blocks
        percent_last = get_value(service, "block", "percent")
        if percent_last == "none":
            percent_last = "0.0"
        filesystem.blocks_percent_last = float(percent_last)
        filesystem.blocks_percent = json_list_append(filesystem.blocks_percent, filesystem.blocks_percent_last)

        # inode
        percent_last = get_value(service, "inode", "percent")
        if percent_last == "none":
            percent_last = "0.0"
        filesystem.inode_percent_last = float(percent_last)
        filesystem.inode_percent = json_list_append(filesystem.inode_percent, filesystem.inode_percent_last)

        filesystem.save()
