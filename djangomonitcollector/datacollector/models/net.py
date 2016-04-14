import datetime

from django.db import models
from pytz import timezone

from service import Service
from utils import get_value, get_string, get_int
from djangomonitcollector.datacollector.lib.elastic import publish_to_elasticsearch


# type = 8
class Net(Service):
    server = models.ForeignKey('Server')
    state = models.TextField(null=True)
    speed = models.TextField(null=True)
    duplex = models.TextField(null=True)
    download_packet_sum = models.BigIntegerField(null=True)
    download_bytes_sum = models.BigIntegerField(null=True)
    download_errors_sum = models.BigIntegerField(null=True)
    upload_packet_sum = models.BigIntegerField(null=True)
    upload_bytes_sum = models.BigIntegerField(null=True)
    upload_errors_sum = models.BigIntegerField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        net_name = get_value(service, "", "", "name")
        net, created = cls.objects.get_or_create(server=server, name=net_name)
        net.service_type = get_value(service, "type", "")
        net.name = get_value(service, "", "", "name")
        net.status = get_value(service, "status", "")
        net.status_hint = get_string(service, "status_hint", "")
        net.monitor = get_string(service, "monitor", "")
        net.monitor_mode = get_string(service, "monitormode", "")
        net.pending_action = get_string(service, "pendingaction", "")

        download_packets = get_int(service, "link.download.packets.now", None)
        if download_packets:
            net.download_packet = download_packets
            net.download_packet_sum = get_int(service, "link.download.packets.total", None)
            net.download_bytes = get_int(service, "link.download.bytes.now", None)
            net.download_bytes_sum = get_int(service, "link.download.bytes.total", None)
            net.download_errors = get_int(service, "link.download.errors.total", None)
            net.download_errors_sum = get_int(service, "link.download.errors.total", None)
            net.upload_packet = get_int(service, "link.upload.packets.now", None)
            net.upload_packet_sum = get_int(service, "link.upload.packets.total", None)
            net.upload_bytes = get_int(service, "link.upload.bytes.now", None)
            net.upload_bytes_sum = get_int(service, "link.upload.bytes.total", None)
            net.upload_errors = get_int(service, "link.upload.errors.total", None)
            net.upload_errors_sum = get_int(service, "link.upload.errors.total", None)
            net.state = get_string(service, "state", None)
            net.duplex = get_string(service, "duplex", None)
            net.speed = get_string(service, "speed", None)

        net.save()
        if download_packets:
            collect_timestamp = int(get_value(service, "collected_sec", ""))
            try:
                entry = NetStats.create(
                        net,
                        net.server.data_timezone,
                        collect_timestamp,
                        net.download_packet,
                        net.download_bytes,
                        net.download_errors,
                        net.upload_packet,
                        net.upload_bytes,
                        net.upload_errors
                )

                NetStats.to_elasticsearch(
                    entry,
                    net.server.localhostname.replace('.','_'),
                    net.name
                    )

            except ValueError as e:
                print "{0}:{1}".format(e.args, e.message)
            except NameError as e:
                print "{0}:{1}".format(e.args, e.message)
        return net



    @classmethod
    def get_by_name(cls, server, name):
        service, created = cls.objects.get_or_create(server=server, name=name)
        return service


class NetStats(models.Model):
    net_id = models.ForeignKey('Net')
    date_last = models.DateTimeField()
    download_packet = models.IntegerField(null=True)
    download_bytes = models.IntegerField(null=True)
    download_errors = models.IntegerField(null=True)
    upload_packet = models.IntegerField(null=True)
    upload_bytes = models.IntegerField(null=True)
    upload_errors = models.IntegerField(null=True)

    @classmethod
    def create(cls,
               net,
               tz_str,
               unixtimestamp,
               download_packet,
               download_bytes,
               download_errors,
               upload_packet,
               upload_bytes,
               upload_errors,
               ):
        entity = cls(net_id=net)
        tz = timezone(tz_str)
        entity.date_last = datetime.datetime.fromtimestamp(unixtimestamp, tz)
        entity.download_bytes = download_bytes
        entity.download_errors = download_errors
        entity.download_packet = download_packet
        entity.upload_bytes = upload_bytes
        entity.upload_errors = upload_errors
        entity.upload_packet = upload_packet
        entity.save()
        return entity

    @classmethod
    def to_elasticsearch(cls, entry, server_name, net):
        _doc = dict()
        _doc['timestamp'] = entry.date_last
        _doc['{}_net_{}_download_packet'.format(server_name, net)] = entry.download_packet
        _doc['{}_net_{}_download_bytes'.format(server_name, net)] = entry.download_bytes
        _doc['{}_net_{}_download_errors'.format(server_name, net)] = entry.download_errors
        _doc['{}_net_{}_upload_packet'.format(server_name, net)] = entry.upload_packet
        _doc['{}_net_{}_upload_bytes'.format(server_name, net)] = entry.upload_bytes
        _doc['{}_net_{}_upload_errors'.format(server_name, net)] = entry.upload_errors

        publish_to_elasticsearch(
            "monit",
            "net-stats",
            _doc
            )
