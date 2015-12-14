from django.db import models

from service import Service
from utils import get_value, decode_status, get_string, get_int


# type = 8
class Net(Service):
    server = models.ForeignKey('Server')
    date_last = models.PositiveIntegerField(null=True)
    state = models.IntegerField(null=True)
    speed = models.IntegerField(null=True)
    duplex = models.IntegerField(null=True)

    download_packet = models.IntegerField(null=True)
    download_packet_sum = models.IntegerField(null=True)
    download_bytes = models.IntegerField(null=True)
    download_bytes_sum = models.IntegerField(null=True)
    download_errors = models.IntegerField(null=True)
    download_errors_sum = models.IntegerField(null=True)

    upload_packet = models.IntegerField(null=True)
    upload_packet_sum = models.IntegerField(null=True)
    upload_bytes = models.IntegerField(null=True)
    upload_bytes_sum = models.IntegerField(null=True)
    upload_errors = models.IntegerField(null=True)
    upload_errors_sum = models.IntegerField(null=True)

    @classmethod
    def update(cls, xmldoc, server, service):
        net_name = get_value(service, "", "", "name")
        net, created = cls.objects.get_or_create(server=server, name=net_name)
        net.name = get_value(service, "", "", "name")
        net.status = decode_status(int(get_value(service, "status", "")))
        net.status_hint = get_string(service, "status_hint", "")
        net.monitor = get_string(service, "monitor", "")
        net.monitormode = get_string(service, "monitormode", "")
        net.pendingaction = get_string(service, "pendingaction", "")

        net.download_packet = get_int(service, "link.download.packets.now", None)
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

        net.state = get_int(service, "state", None)
        net.duplex = get_int(service, "duplex", None)
        net.speed = get_int(service, "speed", None)

        net.save()
