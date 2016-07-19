from pytz import timezone
import datetime
import json

from ..broker import to_queue
from djangomonitcollector.datacollector.lib.elastic import publish_to_elasticsearch
from djangomonitcollector.datacollector.lib.graphite import collect_metric_from_datetime
from djangomonitcollector.ui.templatetags.extra_tags import percent_to_bar, kb_formatting


class NetMetric(object):
    download_bytes = None
    download_errors = None
    download_packet = None
    upload_bytes = None
    upload_errors = None
    upload_packet = None


class NetMetrics(object):

    metric = NetMetric()
    server_name = None
    server_id = None
    net_name = None

    def __init__(self,
                 server,
                 net,
                 timestamp):

        tz = timezone(server.data_timezone)
        self.metric.date_last = datetime.datetime.fromtimestamp(timestamp, tz)
        self.metric.download_bytes = net.download_bytes
        self.metric.download_errors = net.download_errors
        self.metric.download_packet = net.download_packet
        self.metric.upload_bytes = net.upload_bytes
        self.metric.upload_errors = net.upload_errors
        self.metric.upload_packet = net.upload_packet
        self.server_name = server.localhostname.replace('.', '_')
        self.server_id = server.id

        self.net_name = net.name

    def to_carbon(self):
        metric = "{}.net.{}.download.packet".format(
            self.server_name, self.net_name)
        collect_metric_from_datetime(
            metric, self.metric.download_packet, self.metric.date_last)

        metric = "{}.net.{}.download.bytes".format(
            self.server_name, self.net_name)
        collect_metric_from_datetime(
            metric, self.metric.download_bytes, self.metric.date_last)

        metric = "{}.net.{}.download.errors".format(
            self.server_name, self.net_name)
        collect_metric_from_datetime(
            metric, self.metric.download_errors, self.metric.date_last)

        metric = "{}.net.{}.upload.packet".format(
            self.server_name, self.net_name)
        collect_metric_from_datetime(
            metric, self.metric.upload_packet, self.metric.date_last)

        metric = "{}.net.{}.upload.bytes".format(
            self.server_name, self.net_name)
        collect_metric_from_datetime(
            metric, self.metric.upload_bytes, self.metric.date_last)

        metric = "{}.net.{}.upload.errors".format(
            self.server_name, self.net_name)
        collect_metric_from_datetime(
            metric, self.metric.upload_errors, self.metric.date_last)

    def to_elasticsearch(self):
        _doc = dict()
        _doc['timestamp'] = self.metric.date_last
        _doc['{}_net_{}_download_packet'.format(
            self.server_name, self.net_name)] = self.metric.download_packet
        _doc['{}_net_{}_download_bytes'.format(
            self.server_name, self.net_name)] = self.metric.download_bytes
        _doc['{}_net_{}_download_errors'.format(
            self.server_name, self.net_name)] = self.metric.download_errors
        _doc['{}_net_{}_upload_packet'.format(
            self.server_name, self.net_name)] = self.metric.upload_packet
        _doc['{}_net_{}_upload_bytes'.format(
            self.server_name, self.net_name)] = self.metric.upload_bytes
        _doc['{}_net_{}_upload_errors'.format(
            self.server_name, self.net_name)] = self.metric.upload_errors

        publish_to_elasticsearch(
            "monit",
            "net-stats",
            _doc
        )
