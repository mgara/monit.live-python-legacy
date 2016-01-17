from xml.dom import minidom
import datetime

from django.db import models
from pytz import timezone

from service import Service

from process import Process
from system import System
from net import Net
from filesystem import FileSystem
from platform import Platform
from file import File
from url import Host
from program import Program
from utils import remove_old_services, get_value,get_string,TIMEZONES_CHOICES
from djangomonitcollector.users.models import CollectorKey, User


class CollectorKeyError(Exception):
    def __init__(self, message):
        self.message = message


class Server(models.Model):
    monit_id = models.CharField(max_length=32, unique=True)
    user_id = models.ForeignKey(User)

    monit_version = models.TextField(null=True)
    localhostname = models.TextField(null=True)
    uptime = models.IntegerField(null=True)
    address = models.TextField(null=True)

    http_address = models.CharField(max_length=200, null=True)
    http_username = models.CharField(max_length=45, default="monit")
    http_password = models.CharField(max_length=45, default="admin")
    monit_update_period = models.IntegerField(default=60)
    data_timezone = models.CharField(max_length=30, choices=TIMEZONES_CHOICES, default='America/Montreal')

    is_new = models.BooleanField(default=True)

    @classmethod
    def update(cls, xmldoc, monit_id, user):
        reporting_services = []
        server, created = cls.objects.get_or_create(monit_id=monit_id, user_id=user)
        server.monit_version = xmldoc.getElementsByTagName(
            'monit')[0].attributes["version"].value
        server.localhostname = get_value(xmldoc, "localhostname", "")
        server.uptime = get_value(xmldoc, "server", "uptime")
        server.address = get_value(xmldoc, "server", "address")
        server.save()

        Platform.update(xmldoc, server)

        event_doc = xmldoc.getElementsByTagName('event')
        event_service = None
        event_service_name = None
        if event_doc:
            event_xml = event_doc[0]
            event_service_name = get_string(event_xml, "service", "")

        if not server.is_new:
            for service in xmldoc.getElementsByTagName('services')[0].getElementsByTagName('service'):
                service_type = get_value(service, "type", "")
                service_name = get_value(service, "", "", "name")
                reporting_services.append(service_name)

                if service_type == '0':  # Filesystem
                    p = FileSystem.update(xmldoc, server, service)
                    if service_name == event_service_name:
                        event_service = p
                elif service_type == '2':  # File
                    p = File.update(xmldoc, server, service)
                    if service_name == event_service_name:
                        event_service = p
                elif service_type == '3':  # Process
                    p = Process.update(xmldoc, server, service)
                    if service_name == event_service_name:
                        event_service = p
                elif service_type == '4':  # Host
                    p = Host.update(xmldoc, server, service)
                    if service_name == event_service_name:
                        event_service = p
                elif service_type == '5':  # System Analysis
                    p = System.update(xmldoc, server, service)
                    if "Monit" == event_service_name:
                        event_service = p
                elif service_type == '7':  # Program
                    p = Program.update(xmldoc, server, service)
                    if service_name == event_service_name:
                        event_service = p
                elif service_type == '8':  # Network Card
                    p = Net.update(xmldoc, server, service)
                    if service_name == event_service_name:
                        event_service = p
                else:
                    p = Process.update(xmldoc, server, service)
                    if service_name == event_service_name:
                        event_service = p
            remove_old_services(server, reporting_services)
        else:
            raise StandardError("New Server, you must configure it in your server settings")

        if event_service == None:
            event_service = System.get_system_service(server)
        if event_doc:
            MonitEvent.create(
                event_xml,
                server,
                event_service
            )


def collect_data(xml_str, ck):
    try:
        xmldoc = minidom.parseString(xml_str)
        monit_id = xmldoc.getElementsByTagName(
            'monit')[0].attributes["id"].value
    except:
        return False, "Problem parsing the xml document"
    try:
        ckobj = CollectorKey.objects.get(pk=ck)
        if ckobj:
            if ckobj.is_enabled:
                Server.update(xmldoc, monit_id, ckobj.user_id)
            else:
                raise CollectorKeyError("Key Not Active {0}".format(ck))
        else:
            raise CollectorKeyError("No Such Key Error {0}".format(ck))
    except StandardError as e:
        return False, "Error While updating the server instance: {0}".format(e.message)
    return True, "Server instance Updated"


class MonitEvent(models.Model):
    server = models.ForeignKey(Server)
    service = models.ForeignKey(Service)
    event_type = models.PositiveIntegerField(null=True)
    event_id = models.PositiveIntegerField(null=True)
    event_state = models.PositiveIntegerField(null=True)
    event_action = models.PositiveIntegerField(null=True)
    event_message = models.TextField(null=True)
    event_time = models.DateTimeField(null=True)
    is_ack = models.BooleanField(default=False)

    @classmethod
    def create(cls, xml_doc, server, service):
        event_obj = cls(
            server=server,
            service=service
        );

        tz = timezone(server.data_timezone)
        unix_timestamp = "{0}.{1}".format(get_value(xml_doc, "collected_sec", ""),
                                          get_value(xml_doc, "collected_usec", ""))
        event_obj.event_type = get_value(xml_doc, "type", "")
        event_obj.event_id = int(get_value(xml_doc, "id", ""))
        event_obj.event_state = int(get_value(xml_doc, "state", ""))
        event_obj.event_action = int(get_value(xml_doc, "action", ""))
        event_obj.event_message = get_value(xml_doc, "message", "")
        event_obj.event_time = datetime.datetime.fromtimestamp(float(unix_timestamp)).replace(tzinfo=tz)
        event_obj.save()
        return event_obj
