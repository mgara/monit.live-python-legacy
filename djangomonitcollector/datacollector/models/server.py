from xml.dom import minidom
import sys

from django.db import models

from process import Process
from system import System
from net import Net
from filesystem import FileSystem
from platform import Platform
from file import File
from url import Host
from program import Program
from utils import remove_old_services, get_value,TIMEZONES_CHOICES
from djangomonitcollector.users.models import CollectorKey,User


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

    http_address = models.CharField(max_length=200,null=True)
    http_username = models.CharField(max_length=45,default="monit")
    http_password = models.CharField(max_length=45,default="admin")
    monit_update_period = models.IntegerField(default=60)
    data_timezone = models.CharField(max_length=30,choices=TIMEZONES_CHOICES, default='America/Montreal')

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
        if not server.is_new:
            for service in xmldoc.getElementsByTagName('services')[0].getElementsByTagName('service'):
                service_type = get_value(service, "type", "")
                service_name = get_value(service, "", "", "name")
                reporting_services.append(service_name)

                if service_type == '0':  # Filesystem
                    FileSystem.update(xmldoc, server, service)
                elif service_type == '2':  # File
                    File.update(xmldoc, server, service)
                elif service_type == '3':  # Process
                    Process.update(xmldoc, server, service)
                elif service_type == '4':  # Host
                    Host.update(xmldoc, server, service)
                elif service_type == '5':  # System Analysis
                    System.update(xmldoc, server, service)
                elif service_type == '7':  # Program
                    Program.update(xmldoc, server, service)
                elif service_type == '8':  # Network Card
                    Net.update(xmldoc, server, service)
                else:
                    Process.update(xmldoc, server, service)
            remove_old_services(server, reporting_services)
        else:
            raise StandardError("New Server, you must configure it in your server settings")

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
