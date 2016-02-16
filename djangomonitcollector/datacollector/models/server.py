import ast
import datetime
import importlib
import logging
import re
from datetime import timedelta
from threading import Thread

from django.conf import settings
from django.db import models
from pytz import timezone

from djangomonitcollector.users.models import User
from file import File
from filesystem import FileSystem
from net import Net
from platform import Platform
from process import Process
from program import Program
from service import Service
from system import System
from url import Host
from utils import \
    remove_old_services, \
    get_value, \
    get_int, \
    get_string, \
    TIMEZONES_CHOICES

# Get an instance of a logger
logger = logging.getLogger(__name__)


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
    def update(cls, xmldoc, monit_id, user, external_ip, manual_approval_required):
        reporting_services = []
        server, created = cls.objects.get_or_create(
                monit_id=monit_id, user_id=user)

        dom_element = xmldoc.getElementsByTagName(
                'monit')[0]
        externalevent = "externalevent" in dom_element.attributes.keys()

        if not externalevent:
            port = get_int(xmldoc, "server.httpd.port")
            port_str = ":{0}".format(port) if port != 80 else ""
            protocol = "https" if get_int(xmldoc, "server.httpd.ssl") == 1 else "http"
            address = server.address if server.address != "0.0.0.0" else external_ip
            server.last_data_received = datetime.datetime.utcnow().replace(tzinfo=timezone("UTC"))
            server.monit_version = xmldoc.getElementsByTagName(
                    'monit')[0].attributes["version"].value
            server.external_ip = external_ip
            server.localhostname = get_value(xmldoc, "localhostname", "")
            server.uptime = get_value(xmldoc, "server", "uptime")
            server.address = get_string(xmldoc, "server.httpd.address")
            server.http_address = "{0}://{1}{2}/".format(protocol, address, port_str)
            server.http_username = get_string(xmldoc, "server.credentials.username")
            server.http_password = get_string(xmldoc, "server.credentials.password")
            server.monit_update_period = get_int(xmldoc, "server.poll")
            server.save()

            Platform.update(xmldoc, server)

        event_doc = xmldoc.getElementsByTagName('event')

        if event_doc:
            event_xml = event_doc[0]

            MonitEvent.create(
                    event_xml,
                    server,
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, xml_doc, server):

        # Parse XML
        tz = timezone(server.data_timezone)
        unix_timestamp = "{0}.{1}".format(get_value(xml_doc, "collected_sec", ""),
                                          get_value(xml_doc, "collected_usec", ""))
        event_time = datetime.datetime.fromtimestamp(
                float(unix_timestamp)).replace(tzinfo=tz)

        event_service_name = get_string(xml_doc, "service", "")
        event_type = get_value(xml_doc, "type", "")
        event_id = int(get_value(xml_doc, "id", ""))
        event_state = int(get_value(xml_doc, "state", ""))
        event_action = int(get_value(xml_doc, "action", ""))
        event_message = get_value(xml_doc, "message", "")
        # Get Service Id from service name
        event_service = get_service_by_name(server, event_type, event_service_name)

        # Create and Save Event Entity
        event_obj = cls(
                server=server,
                service=event_service
        )
        event_obj.event_type = event_type
        event_obj.event_id = event_id
        event_obj.event_state = event_state
        event_obj.event_action = event_action
        event_obj.event_message = event_message
        event_obj.event_time = event_time
        event_obj.save()

        # Detect if Service is flapping
        cls.detect_service_flapping(event_obj, server)

        # Check if we received Monit Stopped Event
        cls.update_server_running_status(event_obj, server)

        # Process event into notifications
        thread = Thread(target=process_event, args=(event_obj,))
        thread.start()

        return event_obj

    @classmethod
    def update_server_running_status(cls, event_obj, server):
        pattern = re.compile("^Monit.*stopped$")
        server.server_up = True
        if event_obj.event_action == 3 and pattern.match(event_obj.event_message):
            server.server_up = False
        server.save()

    @classmethod
    def detect_service_flapping(cls, evt, server):
        event_service = evt.service
        if int(evt.event_type) != 3:
            return
        try:
            server_tz = timezone("UTC")
            now = datetime.datetime.utcnow().replace(tzinfo=server_tz)
            flapping_period = timedelta(seconds=settings.SERVICE_FLAPPING_PERIOD)  # Between 0 and 86399 inclusive
            start_time = now - flapping_period
            process_state_change_events = MonitEvent.objects.filter(
                    server=server,
                    service=event_service,
                    created_at__gt=start_time
            ).order_by('event_time')

            service_transition = 0
            up = 1
            for event in process_state_change_events:
                if event.event_id == 512 and event.event_state == 1:
                    if up == 1:
                        up = 0
                        service_transition += 1
                if event.event_id == 512 and event.event_state == 0:
                    if up == 0:
                        up = 1
                if event.event_id == 4 and "restarted" in event.event_message:
                    service_transition += 1

            if service_transition >= settings.NUMBER_OF_TRANSITIONS_PER_FLAPPING_PERIOD:
                if not event_service.is_flapping:
                    event_service.is_flapping = True
            else:
                if event_service.is_flapping:
                    event_service.is_flapping = False

            event_service.save()
        except StandardError as e:
            print e

    @classmethod
    def mute(cls, event_object):
        event_object.is_ack = True
        event_object.save()

    def __str__(self):
        return "Monit Event For {0}".format(self.service)


def process_event(event_object):
    user = event_object.server.user_id
    # TODO: execute mute notifications first.
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


def get_service_by_name(server, event_type, service_name):
    '''

    :param server:
    :param event_type:
    :param service_name:
    :return:  service
    '''

    if "Monit" in service_name:
        return System.get_by_server(server)

    event_type = int(event_type)

    if event_type == 0:
        return FileSystem.get_by_name(server, service_name)
    if event_type == 2:
        return File.get_by_name(server, service_name)
    if event_type == 3:
        return Process.get_by_name(server, service_name)
    if event_type == 4:
        return Host.get_by_name(server, service_name)
    if event_type == 5:
        return System.get_by_server(server)
    if event_type == 7:
        return Program.get_by_name(server, service_name)
    if event_type == 8:
        return Net.get_by_name(server, service_name)

    return System.get_by_server(server)
