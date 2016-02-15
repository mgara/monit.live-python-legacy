from xml.dom import minidom
import datetime
import ast
import re
import importlib

from django.db import models
from pytz import timezone

from service import Service
from threading import Thread

from process import Process
from system import System
from net import Net
from filesystem import FileSystem
from platform import Platform
from file import File
from url import Host
from program import Program
from django.conf import settings


from utils import \
    remove_old_services, \
    get_value,\
    get_int,\
    get_string,\
    TIMEZONES_CHOICES

from djangomonitcollector.users.models import \
    CollectorKey, \
    User


def collect_data(xml_str, ck, ip_addr):
    try:
        xmldoc = minidom.parseString(xml_str)
        monit_id = xmldoc.getElementsByTagName(
            'monit')[0].attributes["id"].value
    except:
        return False, "Problem parsing the xml document"

    multi_tenant = settings.ENABLE_MULTI_TENANT
    manual_approval_required = settings.ENABLE_MANUAL_APPROVAL

    try:
        if multi_tenant:
            ckobj = CollectorKey.objects.get(pk=ck)
            if ckobj:
                if ckobj.is_enabled:
                    Server.update(
                        xmldoc,
                        monit_id,
                        ckobj.user_id,
                        ip_addr,
                        manual_approval_required
                    )
                else:
                    raise CollectorKeyError("Key Not Active {0}".format(ck))
            else:
                raise CollectorKeyError("No Such Key Error {0}".format(ck))
        else:
            default_user = User.objects.all()[0]  # first user
            Server.update(
                xmldoc,
                monit_id,
                default_user,
                ip_addr,
                manual_approval_required
            )

    except StandardError as e:
        return False, "Error While updating the server instance: {0}".format(e.message)
    return True, "Server instance Updated"


class CollectorKeyError(Exception):

    def __init__(self, message):
        self.message = message


class Server(models.Model):
    user_id = models.ForeignKey(User)

    address = models.TextField(null=True)
    data_timezone = models.CharField(max_length=30, choices=TIMEZONES_CHOICES, default=settings.TIME_ZONE)
    external_ip = models.TextField(null=True)
    http_address = models.CharField(max_length=200, null=True)
    http_password = models.CharField(max_length=45, default="admin")
    http_username = models.CharField(max_length=45, default="monit")
    disable_monitoring = models.BooleanField(default=True)
    localhostname = models.TextField(null=True)
    monit_id = models.CharField(max_length=32, unique=True)
    monit_update_period = models.IntegerField(default=60)
    monit_version = models.TextField(null=True)
    server_up = models.BooleanField(default=True)
    uptime = models.IntegerField(null=True)
    last_data_received = models.DateTimeField()
    

    @classmethod
    def update(cls, xmldoc, monit_id, user,external_ip, manual_approval_required):
        reporting_services = []
        server, created = cls.objects.get_or_create(
            monit_id=monit_id, user_id=user)
        
        dom_element = xmldoc.getElementsByTagName(
                        'monit')[0]
        externalevent = "externalevent" in dom_element.attributes.keys()
        if not externalevent:
            port = get_int(xmldoc,"server.httpd.port")
            port_str = ":{0}".format(port) if port != 80 else ""
            protocol = "https" if get_int(xmldoc,"server.httpd.ssl") == 1 else "http"
            address = server.address if server.address != "0.0.0.0" else external_ip
            server.last_data_received = datetime.datetime.utcnow().replace(tzinfo=timezone("UTC"))
            server.monit_version = xmldoc.getElementsByTagName(
                'monit')[0].attributes["version"].value
            server.external_ip = external_ip
            server.localhostname = get_value(xmldoc, "localhostname", "")
            server.uptime = get_value(xmldoc, "server", "uptime")
            server.address = get_string(xmldoc,"server.httpd.address")
            server.http_address = "{0}://{1}{2}/".format(protocol,address,port_str)
            server.http_username = get_string(xmldoc,"server.credentials.username")
            server.http_password = get_string(xmldoc,"server.credentials.password")
            server.monit_update_period = get_int(xmldoc,"server.poll")
            server.save()

            Platform.update(xmldoc, server)

        event_doc = xmldoc.getElementsByTagName('event')
        event_service = None
        event_service_name = None

        if event_doc:
            event_xml = event_doc[0]
            event_service_name = get_string(event_xml, "service", "")
            if event_service == None:
                event_service = System.get_system_service(server)
            MonitEvent.create(
                event_xml,
                server,
                event_service
            )
        else:
            if server.disable_monitoring and manual_approval_required:
                raise StandardError(
                    "New Server, you must configure it in your server settings, \
                    or set 'ENABLE_MANUAL_APPROVAL' settings parameter to false ")
            else:
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
        )

        tz = timezone(server.data_timezone)
        unix_timestamp = "{0}.{1}".format(get_value(xml_doc, "collected_sec", ""),
                                          get_value(xml_doc, "collected_usec", ""))
        event_obj.event_type = get_value(xml_doc, "type", "")
        event_obj.event_id = int(get_value(xml_doc, "id", ""))
        event_obj.event_state = int(get_value(xml_doc, "state", ""))
        event_obj.event_action = int(get_value(xml_doc, "action", ""))
        event_obj.event_message = get_value(xml_doc, "message", "")
        event_obj.event_time = datetime.datetime.fromtimestamp(
            float(unix_timestamp)).replace(tzinfo=tz)

        event_obj.save()

        pattern = re.compile("^Monit.*stopped$")
        server.server_up = True
        if event_obj.event_action == 3 and pattern.match(event_obj.event_message):
            server.server_up = False
        server.save()

        thread = Thread(target=process_event, args=(event_obj,))
        thread.start()

        return event_obj

    @classmethod
    def mute(cls, event_object):
        event_object.is_ack = True
        event_object.save()

    def __str__(self):
        return "Monit Event For {0}".format(self.service)


def process_event(event_object):
    user = event_object.server.user_id
    for nt in user.notificationtype_set.all():
        if nt.notification_enabled:
            name_matches = check_item(
                event_object.service.name, nt.notification_service)
            state_matches = check_item(
                event_object.event_state, nt.notification_state)
            action_matches = check_item(
                event_object.event_action, nt.notification_action)
            type_matches = check_item(
                event_object.event_type, nt.notification_type)
            messages_matches = True if re.search(
                nt.notification_message, event_object.event_message) else False

            if name_matches and state_matches and action_matches and type_matches and messages_matches:
                notification_handler_module = importlib.import_module(
                    "djangomonitcollector.notificationsystem.lib.{0}".format(nt.notification_class.lower()))
                class_ = getattr(
                    notification_handler_module, nt.notification_class)
                notification_class_instance = class_()
                notification_class_instance.set_event(event_object)
                notification_class_instance.set_extra_params(
                    nt.notification_plugin_extra_params)
                notification_class_instance.process()


def check_item(item, string_list_of_items):
    if not string_list_of_items.strip():
        return True
    try:
        list_of_items = ast.literal_eval(string_list_of_items)
    except StandardError as e:
        return "Error"
    if len(list_of_items) == 0:
        return True
    if list_of_items is not None:
        if str(item) in list_of_items:
            return True
        return False
    return True
