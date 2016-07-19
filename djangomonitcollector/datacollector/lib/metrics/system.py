from pytz import timezone
import datetime
import json

from ..broker import to_queue
from djangomonitcollector.datacollector.lib.elastic import publish_to_elasticsearch
from djangomonitcollector.datacollector.lib.graphite import collect_metric_from_datetime
from djangomonitcollector.ui.templatetags.extra_tags import percent_to_bar, kb_formatting, time_str


class MemoryCPUSystemMetric(object):
    load_avg01 = None
    load_avg05 = None
    load_avg15 = None
    cpu_user = None
    cpu_system = None
    cpu_wait = None
    memory_kilobyte = None
    memory_percent = None
    swap_percent = None
    swap_kilobyte = None


class MemoryCPUSystemMetrics(object):
    metric = MemoryCPUSystemMetric()
    server_name = None
    server_id = None
    server_uptime = None

    def __init__(self,
                 system,
                 server,
                 timestamp
                 ):
        tz = timezone(server.data_timezone)
        self.metric.date_last = datetime.datetime.fromtimestamp(timestamp, tz)
        self.metric.load_avg01 = system.load_avg01_last
        self.metric.load_avg05 = system.load_avg05_last
        self.metric.load_avg15 = system.load_avg15_last
        self.metric.cpu_user = system.cpu_user_last
        self.metric.cpu_system = system.cpu_system_last
        self.metric.cpu_wait = system.cpu_wait_last
        self.metric.memory_percent = system.memory_percent_last
        self.metric.memory_kilobyte = system.memory_kilobyte_last
        self.metric.swap_percent = system.swap_percent_last
        self.metric.swap_kilobyte = system.swap_kilobyte_last
        self.server_name = server.localhostname.replace('.', '_')
        self.server_id = server.id
        self.server_uptime = server.uptime

        self.to_carbon()
        self.to_elasticsearch()
        self.to_broker()

    def to_carbon(self):
        metric = "{}.system.load.avg01".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.load_avg01, self.metric.date_last)
        metric = "{}.system.load.avg05".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.load_avg05, self.metric.date_last)

        metric = "{}.system.load.avg15".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.load_avg15, self.metric.date_last)

        metric = "{}.system.cpu.user".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.cpu_user, self.metric.date_last)
        metric = "{}.system.cpu.system".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.cpu_system, self.metric.date_last)
        metric = "{}.system.cpu.wait".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.cpu_wait, self.metric.date_last)

        metric = "{}.system.memory.percent".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.memory_percent, self.metric.date_last)
        metric = "{}.system.memory.kilobyte".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.memory_kilobyte, self.metric.date_last)

        metric = "{}.system.swap.percent".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.swap_percent, self.metric.date_last)
        metric = "{}.system.swap.kilobyte".format(
            self.server_name)
        collect_metric_from_datetime(
            metric, self.metric.swap_kilobyte, self.metric.date_last)

    def to_elasticsearch(self):
        _doc = dict()
        _doc['timestamp'] = self.metric.date_last
        _doc['{}_system_load_avg01'.format(
            self.server_name)] = self.metric.load_avg01
        _doc['{}_system_load_avg05'.format(
            self.server_name)] = self.metric.load_avg05
        _doc['{}_system_load_avg15'.format(
            self.server_name)] = self.metric.load_avg15
        _doc['{}_system_cpu_user'.format(
            self.server_name)] = self.metric.cpu_user
        _doc['{}_system_cpu_system'.format(
            self.server_name)] = self.metric.cpu_system
        _doc['{}_system_cpu_wait'.format(
            self.server_name)] = self.metric.cpu_wait
        _doc['{}_system_memory_percent'.format(
            self.server_name)] = self.metric.memory_percent
        _doc['{}_system_memory_kilobyte'.format(
            self.server_name)] = self.metric.memory_kilobyte
        _doc['{}_system_swap_percent'.format(
            self.server_name)] = self.metric.swap_percent
        _doc['{}_system_swap_kilobyte'.format(
            self.server_name)] = self.metric.swap_kilobyte

        publish_to_elasticsearch(
            "monit",
            "system-stats",
            _doc
        )

    def to_broker(self):
        response = dict()
        response['channel'] = str(self.server_id).replace("-", "_")

        response['cpu_user_last'] = self.metric.cpu_user
        response['cpu_system_last'] = self.metric.cpu_user
        response['cpu_wait_last'] = self.metric.cpu_wait

        response['memory_percent_last'] = self.metric.memory_percent
        response['memory_kilobyte_last'] = self.metric.memory_kilobyte

        response['load_avg1_last'] = self.metric.load_avg01
        response['load_avg5_last'] = self.metric.load_avg05
        response['load_avg15_last'] = self.metric.load_avg15

        # formatted
        response['cpu_user_last_progress_bar'] = percent_to_bar(
            self.metric.cpu_user)
        response['cpu_wait_last_progress_bar'] = percent_to_bar(
            self.metric.cpu_wait)
        response['cpu_system_last_progress_bar'] = percent_to_bar(
            self.metric.cpu_system)

        response['memory_last_progress_bar'] = percent_to_bar(
            self.metric.memory_percent)
        response['memory_last_kb_formatted'] = kb_formatting(
            self.metric.memory_kilobyte)

        response['uptime'] = time_str(self.server_uptime)
        response_str = json.dumps(response)
        to_queue(response_str)
