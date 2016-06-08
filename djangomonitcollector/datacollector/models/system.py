import datetime
from djangomonitcollector.datacollector.lib.elastic import publish_to_elasticsearch

from django.db import models
from pytz import timezone
import pika
import json
from service import Service
from ..lib.utils import get_value, json_list_append
from ..models import AggregationPeriod

from django.conf import settings


class System(Service):
    server = models.OneToOneField('Server')
    date_last = models.PositiveIntegerField(null=True)
    date = models.TextField(null=True)
    load_avg01_last = models.FloatField(null=True)
    load_avg05_last = models.FloatField(null=True)
    load_avg15_last = models.FloatField(null=True)
    cpu_user_last = models.FloatField(null=True)
    cpu_system_last = models.FloatField(null=True)
    cpu_wait_last = models.FloatField(null=True)
    memory_percent_last = models.FloatField(null=True)
    memory_kilobyte_last = models.PositiveIntegerField(null=True)
    swap_percent_last = models.FloatField(null=True)
    swap_kilobyte_last = models.PositiveIntegerField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        data_timestamp = int(get_value(service, "collected_sec", ""))

        system, created = cls.objects.get_or_create(server=server)
        system.service_type = get_value(service, "type", "")
        system.name = get_value(service, "", "", "name")
        system.status = get_value(service, "status", "")
        system.status_hint = get_value(service, "status_hint", "")
        system.monitor = get_value(service, "monitor", "")
        system.monitor_mode = get_value(service, "monitormode", "")
        system.pending_action = get_value(service, "pendingaction", "")

        tz = timezone(system.server.data_timezone)

        if get_value(service, "load", "avg01") != "none":
            system.date_last = data_timestamp
            system.date = json_list_append(system.date, system.date_last)
            system.load_avg01_last = float(get_value(service, "load", "avg01"))
            system.load_avg05_last = float(get_value(service, "load", "avg05"))
            system.load_avg15_last = float(get_value(service, "load", "avg15"))
            system.cpu_user_last = float(get_value(service, "cpu", "user"))
            system.cpu_system_last = float(get_value(service, "cpu", "system"))
            system.cpu_wait_last = float(get_value(service, "cpu", "wait"))
            system.memory_percent_last = float(
                get_value(service, "memory", "percent"))
            system.memory_kilobyte_last = int(
                get_value(service, "memory", "kilobyte"))
            system.swap_percent_last = float(
                get_value(service, "swap", "percent"))
            system.swap_kilobyte_last = int(
                get_value(service, "swap", "kilobyte"))
        system.save()
        broadcast_to_websocket_channel(server, system)

        if get_value(service, "load", "avg01") != "none":
            entity = MemoryCPUSystemStats.create(
                system,
                system.server.data_timezone,
                data_timestamp,
                system.load_avg01_last,
                system.load_avg05_last,
                system.load_avg15_last,
                system.cpu_user_last,
                system.cpu_system_last,
                system.cpu_wait_last,
                system.memory_percent_last,
                system.memory_kilobyte_last,
                system.swap_percent_last,
                system.swap_kilobyte_last
            )
            MemoryCPUSystemStats.to_elasticsearch(
                entity,
                system.server.localhostname.replace('.', '_')
                )
        return system

    @classmethod
    def get_by_server(cls, server):
        system, created = cls.objects.get_or_create(server=server)
        return system


class MemoryCPUAggregatedSystemStats(models.Model):
    system_id = models.ForeignKey('System')
    date_last = models.DateTimeField()
    load_avg01 = models.FloatField(null=True)
    load_avg05 = models.FloatField(null=True)
    load_avg15 = models.FloatField(null=True)
    cpu_user = models.FloatField(null=True)
    cpu_system = models.FloatField(null=True)
    cpu_wait = models.FloatField(null=True)
    memory_percent = models.FloatField(null=True)
    memory_kilobyte = models.PositiveIntegerField(null=True)
    swap_percent = models.FloatField(null=True)
    swap_kilobyte = models.PositiveIntegerField(null=True)
    rule_id = models.ForeignKey(AggregationPeriod)

    @classmethod
    def create(cls,
               system,
               tz_str,
               data_timestamp,
               load_avg01,
               load_avg05,
               load_avg15,
               cpu_user,
               cpu_system,
               cpu_wait,
               memory_percent,
               memory_kilobyte,
               swap_percent,
               swap_kilobyte
               ):
        entry = cls(system_id=system)
        tz = timezone(tz_str)
        entry.date_last = datetime.datetime.fromtimestamp(data_timestamp, tz)
        entry.load_avg01 = load_avg01
        entry.load_avg05 = load_avg05
        entry.load_avg15 = load_avg15
        entry.cpu_user = cpu_user
        entry.cpu_system = cpu_system
        entry.cpu_wait = cpu_wait
        entry.memory_percent = memory_percent
        entry.memory_kilobyte = memory_kilobyte
        entry.swap_percent = swap_percent
        entry.swap_kilobyte = swap_kilobyte
        entry.save()
        return entry


class MemoryCPUSystemStats(models.Model):
    system_id = models.ForeignKey('System')
    date_last = models.DateTimeField()
    load_avg01 = models.FloatField(null=True)
    load_avg05 = models.FloatField(null=True)
    load_avg15 = models.FloatField(null=True)
    cpu_user = models.FloatField(null=True)
    cpu_system = models.FloatField(null=True)
    cpu_wait = models.FloatField(null=True)
    memory_percent = models.FloatField(null=True)
    memory_kilobyte = models.PositiveIntegerField(null=True)
    swap_percent = models.FloatField(null=True)
    swap_kilobyte = models.PositiveIntegerField(null=True)

    @classmethod
    def create(cls,
               system,
               tz_str,
               data_timestamp,
               load_avg01,
               load_avg05,
               load_avg15,
               cpu_user,
               cpu_system,
               cpu_wait,
               memory_percent,
               memory_kilobyte,
               swap_percent,
               swap_kilobyte
               ):
        entry = cls(system_id=system)
        tz = timezone(tz_str)
        entry.date_last = datetime.datetime.fromtimestamp(data_timestamp, tz)
        entry.load_avg01 = load_avg01
        entry.load_avg05 = load_avg05
        entry.load_avg15 = load_avg15
        entry.cpu_user = cpu_user
        entry.cpu_system = cpu_system
        entry.cpu_wait = cpu_wait
        entry.memory_percent = memory_percent
        entry.memory_kilobyte = memory_kilobyte
        entry.swap_percent = swap_percent
        entry.swap_kilobyte = swap_kilobyte
        entry.save()
        return entry

    @classmethod
    def to_elasticsearch(cls, entry, server_name):
        _doc = dict()
        _doc['timestamp'] = entry.date_last
        _doc['{}_system_load_avg01'.format(server_name)] = entry.load_avg01
        _doc['{}_system_load_avg05'.format(server_name)] = entry.load_avg05
        _doc['{}_system_load_avg15'.format(server_name)] = entry.load_avg15
        _doc['{}_system_cpu_user'.format(server_name)] = entry.cpu_user
        _doc['{}_system_cpu_system'.format(server_name)] = entry.cpu_system
        _doc['{}_system_cpu_wait'.format(server_name)] = entry.cpu_wait
        _doc['{}_system_memory_percent'.format(server_name)] = entry.memory_percent
        _doc['{}_system_memory_kilobyte'.format(server_name)] = entry.memory_kilobyte
        _doc['{}_system_swap_percent'.format(server_name)] = entry.swap_percent
        _doc['{}_system_swap_kilobyte'.format(server_name)] = entry.swap_kilobyte

        publish_to_elasticsearch(
            "monit",
            "system-stats",
            _doc
            )


def broadcast_to_websocket_channel(server, system):
    response = dict()
    response['channel'] = "server_dashboard_{0}".format(server.id)
    response['cpu_user_last'] = system.cpu_user_last
    response['cpu_system_last'] = system.cpu_user_last
    response['cpu_wait_last'] = system.cpu_wait_last
    response['memory_percent_last'] = system.memory_percent_last
    response['memory_kilobyte_last'] = system.memory_kilobyte_last
    response_str = json.dumps(response)
    to_queue(response_str)


def to_queue(message):

    rabbitmq_resource = getattr(
        settings, 'BROKER_URL', 'amqp://dmc:va2root@172.16.5.83:5672/%2f')
    rabbitmq_queue = getattr(settings, 'RABBITMQ_QUEUE', 'dmc')
    parameters = pika.URLParameters(rabbitmq_resource)

    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(
        queue=rabbitmq_queue, durable=True, exclusive=False, auto_delete=False)

    # Enabled delivery confirmations
    channel.confirm_delivery()

    channel.basic_publish(exchange='dmc',
                          routing_key='dmc',
                          body=message)

    connection.close()
