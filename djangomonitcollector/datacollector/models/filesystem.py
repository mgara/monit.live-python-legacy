from django.db import models
import time
from service import Service
from utils import get_value, get_float
from pytz import timezone
import datetime

class FileSystem(Service):
    server = models.ForeignKey('Server')
    date_last = models.PositiveIntegerField(null=True)
    file_system = models.TextField(null=True)
    mode = models.TextField(null=True)
    flags = models.IntegerField(null=True)
    blocks_total = models.TextField(null=True)
    inode_total = models.TextField(null=True)
    blocks_percent_last = models.FloatField(null=True)
    blocks_usage_last = models.IntegerField(null=True)
    inode_percent_last = models.FloatField(null=True)
    inode_usage_last = models.IntegerField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        fs_name = get_value(service, "", "", "name")
        fs_name.replace('_', '')
        filesystem, created = cls.objects.get_or_create(server=server, name=fs_name)
        filesystem.service_type = get_value(service, "type", "")
        filesystem.name = fs_name
        filesystem.status = get_value(service, "status", "")
        filesystem.status_hint = get_value(service, "status_hint", "")
        filesystem.monitor = get_value(service, "monitor", "")
        filesystem.monitormode = get_value(service, "monitormode", "")
        filesystem.pendingaction = get_value(service, "pendingaction", "")
        percent_last = get_float(service, "block.percent")
        if percent_last:
            filesystem.blocks_percent_last = percent_last
            filesystem.inode_percent_last = get_float(service, "inode.percent")

        filesystem.save()

        if percent_last :
            colect_timestamp = int(get_value(service, "collected_sec", ""))
            FsAndDiskUsageStats.create(
                filesystem,
                filesystem.server.data_timezone,
                colect_timestamp,
                filesystem.blocks_percent_last,
                filesystem.blocks_usage_last,
                filesystem.inode_percent_last,
                filesystem.inode_usage_last
            )

class FsAndDiskUsageStats(models.Model):
    fs_id = models.ForeignKey('FileSystem')
    date_last = models.DateTimeField(null=False)
    blocks_percent = models.FloatField(null=True)
    blocks_usage = models.IntegerField(null=True)
    inode_percent = models.FloatField(null=True)
    inode_usage = models.IntegerField(null=True)

    #'US/Eastern'
    @classmethod
    def create(cls,fs,tz_str,unixtimestamp, blocks_percent, blocks_usage, inode_percent, inode_usage):
        entry = cls(fs_id=fs)
        tz = timezone(tz_str)
        entry.date_last= datetime.datetime.fromtimestamp(unixtimestamp).replace(tzinfo=tz)
        entry.blocks_percent = blocks_percent
        entry.blocks_usage = blocks_usage
        entry.inode_percent  = inode_percent
        entry.inode_usage = inode_usage
        entry.save()
        return entry