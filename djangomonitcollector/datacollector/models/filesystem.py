import datetime
import json
import calendar

from django.db import models
from pytz import timezone

from service import Service
from ..lib.utils import get_value, get_float
from system import to_queue
from djangomonitcollector.datacollector.lib.elastic import publish_to_elasticsearch


class FileSystem(Service):
    server = models.ForeignKey('Server')
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
        fs_name.replace('_', '')
        filesystem, created = cls.objects.get_or_create(
            server=server, name=fs_name)
        filesystem.service_type = get_value(service, "type", "")
        filesystem.name = fs_name
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
            entry = FsAndDiskUsageStats.create(
                filesystem,
                filesystem.server.data_timezone,
                colect_timestamp,
                filesystem.blocks_percent_last,
                filesystem.blocks_usage_last,
                filesystem.inode_percent_last,
                filesystem.inode_usage_last
            )
            fs_name = filesystem.name.replace('___', '/').replace('_', '/')
            FsAndDiskUsageStats.to_elasticsearch(
                entry,
                filesystem.server.localhostname.replace('.', '_'),
                fs_name
            )

        if filesystem.name == '___':
            broadcast_to_websocket_channel(server, filesystem)
        return filesystem

    @classmethod
    def get_by_name(cls, server, name):
        service, created = cls.objects.get_or_create(server=server, name=name)
        return service


class FsAndDiskUsageStats(models.Model):
    fs_id = models.ForeignKey('FileSystem')
    date_last = models.DateTimeField(null=False)
    blocks_percent = models.FloatField(null=True)
    blocks_usage = models.FloatField(null=True)
    inode_percent = models.FloatField(null=True)
    inode_usage = models.FloatField(null=True)

    @classmethod
    def create(
        cls,
        fs,
        tz_str,
        unixtimestamp,
        blocks_percent,
        blocks_usage,
        inode_percent,
        inode_usage
    ):

        entry = cls(fs_id=fs)
        tz = timezone(tz_str)
        entry.date_last = datetime.datetime.fromtimestamp(unixtimestamp, tz)
        entry.blocks_percent = blocks_percent
        entry.blocks_usage = blocks_usage
        entry.inode_percent = inode_percent
        entry.inode_usage = inode_usage
        entry.save()
        return entry

    @classmethod
    def to_elasticsearch(cls, entry, server_name, fs_name):
        _doc = dict()
        _doc['timestamp'] = entry.date_last
        _doc['{}_fs_{}_blocks_percent'.format(
            server_name, fs_name)] = entry.blocks_percent
        _doc['{}_fs_{}_blocks_usage'.format(
            server_name, fs_name)] = entry.blocks_usage
        _doc['{}_fs_{}_inode_percent'.format(
            server_name, fs_name)] = entry.inode_percent
        _doc['{}_fs_{}_inode_usage'.format(
            server_name, fs_name)] = entry.inode_usage

        publish_to_elasticsearch(
            "monit",
            "filesystem-stats",
            _doc
        )

class FsAndDiskDailyUsageStats(models.Model):
    fs_id = models.ForeignKey('FileSystem')
    date_last = models.DateTimeField(null=False)
    blocks_percent = models.FloatField(null=True)
    blocks_usage = models.FloatField(null=True)
    inode_percent = models.FloatField(null=True)
    inode_usage = models.FloatField(null=True)

    @classmethod
    def create(
        cls,
        fs,
        tz_str,
        unixtimestamp,
        blocks_percent,
        blocks_usage,
        inode_percent,
        inode_usage
    ):

        entry = cls(fs_id=fs)
        tz = timezone(tz_str)
        entry.date_last = datetime.datetime.fromtimestamp(unixtimestamp, tz)
        entry.blocks_percent = blocks_percent
        entry.blocks_usage = blocks_usage
        entry.inode_percent = inode_percent
        entry.inode_usage = inode_usage
        entry.save()
        return entry


def broadcast_to_websocket_channel(server, fs):
    response = dict()
    response['channel'] = "server_dashboard_{0}".format(server.id)
    response['fs_blocks_percent_last'] = fs.blocks_percent_last
    response['fs_blocks_total'] = fs.blocks_total
    response_str = json.dumps(response)
    to_queue(response_str)



