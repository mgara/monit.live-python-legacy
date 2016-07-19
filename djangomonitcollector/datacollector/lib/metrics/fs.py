from pytz import timezone
import datetime
import json

from ..broker import to_queue
from djangomonitcollector.datacollector.lib.elastic import publish_to_elasticsearch
from djangomonitcollector.datacollector.lib.graphite import collect_metric_from_datetime
from djangomonitcollector.ui.templatetags.extra_tags import percent_to_bar, kb_formatting


class FsAndDiskUsageMetric(object):
    date_last = None
    blocks_percent = None
    blocks_usage = None
    inode_percent = None
    inode_usage = None
    blocks_total = None


class FsAndDiskUsageMetrics(object):

    metric = FsAndDiskUsageMetric()
    server_name = None
    server_id = None
    fs_name = None

    def __init__(self,
                 fs,
                 server,
                 timestamp
                 ):
        tz = timezone(server.data_timezone)
        self.metric.date_last = datetime.datetime.fromtimestamp(
            timestamp, tz)
        self.metric.blocks_percent = fs.blocks_percent_last
        self.metric.blocks_usage = fs.blocks_usage_last
        self.metric.inode_percent = fs.inode_percent_last
        self.metric.inode_usage = fs.inode_usage_last
        self.server_name = server.localhostname.replace('.', '_')
        self.server_id = server.id

        self.metric.blocks_total = fs.blocks_total
        self.fs_name = fs.name

        self.to_carbon()
        self.to_elasticsearch()
        if (fs.display_name == '/'):
            self.to_broker()

    def to_carbon(self):
        metric = "{}.self.metric.{}.blocks_percent".format(
            self.server_name,
            self.fs_name.replace('/', '_')
        )
        collect_metric_from_datetime(
            metric,
            self.metric.blocks_percent,
            self.metric.date_last
        )

        metric = "{}.self.metric.{}.blocks_usage".format(
            self.server_name, self.fs_name.replace('/', '_'))
        collect_metric_from_datetime(
            metric, self.metric.blocks_usage, self.metric.date_last)
        metric = "{}.self.metric.{}.inode_percent".format(
            self.server_name, self.fs_name.replace('/', '_'))
        collect_metric_from_datetime(
            metric, self.metric.inode_percent, self.metric.date_last)
        metric = "{}.self.metric.{}.inode_usage".format(
            self.server_name, self.fs_name.replace('/', '_'))
        collect_metric_from_datetime(
            metric, self.metric.inode_usage, self.metric.date_last)

    def to_elasticsearch(self):
        _doc = dict()
        _doc['timestamp'] = self.metric.date_last
        _doc['{}_fs_{}_blocks_percent'.format(
            self.server_name, self.fs_name)] = self.metric.blocks_percent
        _doc['{}_fs_{}_blocks_usage'.format(
            self.server_name, self.fs_name)] = self.metric.blocks_usage
        _doc['{}_fs_{}_inode_percent'.format(
            self.server_name, self.fs_name)] = self.metric.inode_percent
        _doc['{}_fs_{}_inode_usage'.format(
            self.server_name, self.fs_name)] = self.metric.inode_usage

        publish_to_elasticsearch(
            "monit",
            "filesystem-stats",
            _doc
        )

    def to_broker(self):
        response = dict()
        response['channel'] = str(self.server_id).replace("-", "_")
        response['fs_blocks_percent_last'] = self.metric.blocks_percent
        response['fs_blocks_total'] = self.metric.blocks_total
        response['fs_blocks_usage_last'] = self.metric.blocks_usage
        response['fs_blocks_percent_last_formatted'] = percent_to_bar(
            self.metric.blocks_percent)
        response['fs_blocks_free_percent_last_formatted'] = percent_to_bar(
            100-self.metric.blocks_percent)
        if (self.metric.blocks_total):
            response['fs_blocks_total_formatted'] = kb_formatting(
                self.metric.blocks_total*1024)
        response['fs_blocks_usage_last_formatted'] = kb_formatting(
            self.metric.blocks_usage*1024)
        response_str = json.dumps(response)
        to_queue(response_str)
