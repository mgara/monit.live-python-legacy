from xml.dom import minidom

from django.db import models

from process import Process
from system import System
from net import Net
from filesystem import FileSystem
from platform import Platform
from file import File
from url import Host
from program import Program
from utils import remove_old_services, get_value
import sys


class Server(models.Model):
    monit_id = models.CharField(max_length=32, unique=True)
    monit_version = models.TextField(null=True)
    localhostname = models.TextField(null=True)
    uptime = models.IntegerField(null=True)
    address = models.TextField(null=True)

    @classmethod
    def update(cls, xmldoc, monit_id):
        reporting_services = []
        server, created = cls.objects.get_or_create(monit_id=monit_id)
        server.monit_version = xmldoc.getElementsByTagName(
            'monit')[0].attributes["version"].value
        server.localhostname = get_value(xmldoc, "localhostname", "")
        server.uptime = get_value(xmldoc, "server", "uptime")
        server.address = get_value(xmldoc, "server", "address")
        server.save()
        Platform.update(xmldoc, server)
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


def collect_data(xml_str):
    # only ready data if it has a monit id
    try:
        xmldoc = minidom.parseString(xml_str)
        monit_id = xmldoc.getElementsByTagName(
            'monit')[0].attributes["id"].value
    except:
        return False, "Problem parsing the xml document"
    try:
        Server.update(xmldoc, monit_id)
    except:
        e = sys.exc_info()[0]
        return False, "Error While updating the server instance: {0}".format(e)
    return True, "Server instance Updated"
