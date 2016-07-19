from pytz import timezone
import datetime
import json

from ..broker import to_queue
from djangomonitcollector.datacollector.lib.elastic import publish_to_elasticsearch
from djangomonitcollector.datacollector.lib.graphite import collect_metric_from_datetime
from djangomonitcollector.ui.templatetags.extra_tags import percent_to_bar, kb_formatting


class MemoryCPUProcessMetric(object):
    date_last = None
    cpu_percent = None
    memory_percent = None
    memory_kilobyte = None


class MemoryCPUProcessMetrics(object):
    metric = MemoryCPUProcessMetric()
    server_name = None
    server_id = None
    process_name = None

    def __init__(
            self,
            process,
            server,
            timestamp,
    ):
        tz = timezone(server.data_timezone)
        self.metric.date_last = datetime.datetime.fromtimestamp(timestamp, tz)
        self.metric.process_id = process.id
        self.metric.cpu_percent = process.cpu_percent
        self.metric.memory_kilobyte = process.memory_kilobyte
        self.metric.memory_percent = process.memory_percent
        self.server_name = server.localhostname.replace('.', '_')
        self.server_id = server.id

        self.to_carbon()
        self.to_elasticsearch()
        self.to_broker()

    def to_carbon(self):
        metric = "{}.process.{}.cpu_percent".format(
            self.server_name, self.process_name)
        collect_metric_from_datetime(
            metric, self.metric.cpu_percent, self.metric.date_last)
        metric = "{}.process.{}.memory_percent".format(
            self.server_name, self.process_name)
        collect_metric_from_datetime(
            metric, self.metric.memory_percent, self.metric.date_last)
        metric = "{}.process.{}.memory_kilobyte".format(
            self.server_name, self.process_name)
        collect_metric_from_datetime(
            metric, self.metric.memory_kilobyte, self.metric.date_last)

    def to_elasticsearch(self):
        _doc = dict()
        _doc['timestamp'] = self.metric.date_last
        _doc['{}_process_{}_cpu_percent'.format(self.server_name, self.process_name)] = self.metric.cpu_percent
        _doc['{}_process_{}_memory_percent'.format(self.server_name, self.process_name)] = self.metric.memory_percent
        _doc['{}_process_{}_memory_kilobyte'.format(self.server_name, self.process_name)] = self.metric.memory_kilobyte

        publish_to_elasticsearch(
            "monit",
            "process-stats",
            _doc
            )

    def to_broker(self):
        pass
