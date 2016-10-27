from __future__ import unicode_literals, absolute_import

import ast
import datetime
import importlib
import logging
import re
import hashlib
import random
import uuid

import json
from datetime import timedelta
from pytz import timezone

from django.conf import settings
from django.db import models
from djangomonitcollector.users.models import Organisation, User
from djangomonitcollector.datacollector.lib.event_mappings import \
    type_to_string,\
    event_status_to_string,\
    event_state_to_string,\
    action_to_string

from djangomonitcollector.ui.templatetags.extra_tags import clean

from djangomonitcollector.users.models import HostGroup
from ..lib.event_mappings import EVENT_STATE_CHOICES, EVENT_ID_CHOICES, EVENT_TYPE_CHOICES, EVENT_ACTION_CHOICES
from ..lib.broker import to_queue

from .file import File
from .filesystem import FileSystem
from .directory import Directory
from .net import Net
from .platform import Platform
from .process import Process
from .program import Program
from .service import Service
from .system import System
from .url import Host
from ..lib.utils import \
    remove_old_services, \
    get_value, \
    get_int, \
    get_string, \
    TIMEZONES_CHOICES


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Server(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organisation = models.ForeignKey(Organisation)
    host_group = models.ForeignKey(HostGroup)

    address = models.TextField(null=True)
    data_timezone = models.CharField(
        max_length=30, choices=TIMEZONES_CHOICES)
    external_ip = models.TextField(null=True)
    http_address = models.CharField(max_length=200, null=True)
    http_password = models.CharField(max_length=45, null=True, default="admin")
    http_username = models.CharField(max_length=45, null=True, default="monit")
    disable_monitoring = models.BooleanField(default=True)
    localhostname = models.TextField(
        db_index=True, default="default-hostname", null=True)
    monit_id = models.CharField(max_length=32, unique=True)
    monit_update_period = models.IntegerField(default=60)
    monit_version = models.TextField(null=True)
    server_up = models.BooleanField(default=True)
    uptime = models.IntegerField(null=True)
    last_data_received = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        super(Server, self).save(*args, **kwargs)

    @classmethod
    def update(cls, xmldoc, monit_id, org, external_ip, host_group):

        if host_group:
            hg, created = HostGroup.update(org, host_group)
        else:
            hg, created = HostGroup.update(org, "default")

        auto_accept_new_servers = org.settings.general_auto_add_unknown_servers

        reporting_services = []
        server, created = cls.objects.get_or_create(
            monit_id=monit_id, organisation=org, host_group=hg)

        dom_element = xmldoc.getElementsByTagName(
            'monit')[0]
        externalevent = "externalevent" in dom_element.attributes.keys()

        if not externalevent:
            port = get_int(xmldoc, "server.httpd.port")
            port_str = ":{0}".format(port) if port != 80 else ""
            protocol = "https" if get_int(
                xmldoc, "server.httpd.ssl") == 1 else "http"

            server.last_data_received = datetime.datetime.utcnow().replace(
                tzinfo=timezone("UTC"))
            server.monit_version = xmldoc.getElementsByTagName(
                'monit')[0].attributes["version"].value
            server.server_up = True
            server.external_ip = external_ip if not server.external_ip else server.external_ip
            server.localhostname = get_value(
                xmldoc, "localhostname", "") if not server.localhostname else server.localhostname
            server.data_timezone = org.settings.general_default_timezone_for_servers if not server.data_timezone else server.data_timezone
            server.uptime = get_value(xmldoc, "server", "uptime")
            server.address = get_string(xmldoc, "server.httpd.address")

            server.http_username = get_string(
                xmldoc, "server.credentials.username")
            server.http_password = get_string(
                xmldoc, "server.credentials.password")
            server.http_address = "{0}://{1}:{2}@{3}{4}/".format(
                protocol, server.http_username, server.http_password, server.external_ip, port_str) if not server.http_address else server.http_address

            server.monit_update_period = get_int(xmldoc, "server.poll")
            server.save()

            Platform.update(xmldoc, server)

        event_doc = xmldoc.getElementsByTagName('event')

        if event_doc:
            event_xml = event_doc[0]
            MonitEvent.create(
                event_xml,
                server,
                externalevent
            )

        else:
            if not auto_accept_new_servers:
                if server.disable_monitoring:
                    raise StandardError(
                        "New Server, you must configure it in your server settings, \
                        or set 'ENABLE_MANUAL_APPROVAL' settings parameter to false ")
            else:
                service_groups = dict()
                for service_group in xmldoc.getElementsByTagName('servicegroups')[0].getElementsByTagName('servicegroup'):
                    service_group_name = get_value(
                        service_group, "", "", "name")
                    sg = ServiceGroup.update(service_group_name, server)

                    for service in service_group.getElementsByTagName("service"):
                        service = get_value(service, "", "")
                        service_groups[service] = sg.id

                for service in xmldoc.getElementsByTagName('services')[0].getElementsByTagName('service'):
                    service_type = get_value(service, "type", "")
                    service_name = get_value(service, "", "", "name")
                    reporting_services.append(service_name)

                    if service_type == '0':  # Filesystem
                        s = FileSystem.update(xmldoc, server, service)
                        continue
                    elif service_type == '1':  # Directory
                        s = Directory.update(xmldoc, server, service)
                        continue
                    elif service_type == '2':  # File
                        s = File.update(xmldoc, server, service)
                        continue
                    elif service_type == '3':  # Process
                        s = Process.update(xmldoc, server, service)
                        continue
                    elif service_type == '4':  # Host
                        s = Host.update(xmldoc, server, service)
                        continue
                    elif service_type == '5':  # System Analysis
                        s = System.update(xmldoc, server, service)
                        continue
                    elif service_type == '7':  # Program
                        s = Program.update(xmldoc, server, service)
                        continue
                    elif service_type == '8':  # Network Card
                        s = Net.update(xmldoc, server, service)
                        continue
                    else:
                        s = Process.update(xmldoc, server, service)

                    if s.name in service_groups.keys():
                        s.service_group = service_groups[s.name]
                    else:
                        s.service_group = 0
                    s.save()

                remove_old_services(server, reporting_services)

    def __str__(self):
        return self.localhostname


class ServiceGroup(models.Model):
    slug = models.CharField(max_length=40)
    belongs_to = models.ForeignKey(Server)
    display_name = models.CharField(max_length=40, null=True)

    @classmethod
    def update(cls, slug, server):
        service_group, created = cls.objects.get_or_create(
            slug=slug, belongs_to=server)
        return service_group

    def __str__(self):
        return self.display_name

    def __unicode__(self):
        return self.display_name


class MonitEvent(models.Model):
    server = models.ForeignKey(Server)
    service = models.ForeignKey(Service)
    event_type = models.PositiveIntegerField(
        choices=EVENT_TYPE_CHOICES, null=True)
    event_id = models.PositiveIntegerField(choices=EVENT_ID_CHOICES, null=True)
    event_state = models.PositiveIntegerField(
        choices=EVENT_STATE_CHOICES, null=True)
    event_action = models.PositiveIntegerField(
        choices=EVENT_ACTION_CHOICES, null=True)
    event_message = models.TextField(null=True)
    event_time = models.DateTimeField(null=True)

    alarm_raised = models.BooleanField(default=False)
    is_duplicate_of = models.TextField(null=True)
    cleared_by = models.PositiveIntegerField(null=True)
    is_active = models.BooleanField(default=False)
    cleared_alarms = models.TextField(null=True)

    is_ack = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.__str__()

    @classmethod
    def create(cls, xml_doc, server, externalevent):
        # Parse XML
        tz = timezone(server.data_timezone)
        unix_timestamp = "{}".format(get_value(xml_doc, "collected_sec", ""))
        event_time = datetime.datetime.fromtimestamp(
            float(unix_timestamp), tz)

        event_service_name = get_string(xml_doc, "service", "")
        event_type = get_value(xml_doc, "type", "")
        event_id = int(get_value(xml_doc, "id", ""))
        event_state = int(get_value(xml_doc, "state", ""))
        event_action = int(get_value(xml_doc, "action", ""))
        event_message = get_value(xml_doc, "message", "")

        # Get Service Id from service name
        event_service = get_service_by_name(
            server, event_type, event_service_name)

        # Create and Save Event Entity
        event_obj = cls(
            server=server,
            service=event_service,
        )

        event_obj.event_type = event_type
        event_obj.event_id = event_id
        event_obj.event_state = event_state
        event_obj.event_action = event_action
        event_obj.event_message = event_message
        event_obj.event_time = event_time
        event_obj.externalevent = externalevent

        #  Check if we received Monit Stopped Event
        event_obj = cls.update_server_running_status(event_obj, server)

        #  We received an error alarm
        if event_obj.event_state == 1:
            found, duplicates = cls.check_for_events_in_time_window(
                event_obj
            )
            if found:
                dups = []
                for e in duplicates:
                    dups.append(e.id)
                    break
                event_obj.is_duplicate_of = "{}".format(dups)

            #  If alarm is error type :
            if not found:
                found, active = cls.check_active_alarms(event_obj)
                if found:
                    event_obj.alarm_raised = True
                    event_obj.is_active = False
                else:
                    event_obj.alarm_raised = True
                    event_obj.is_active = True

        event_obj.save()

        #  We received a clear alarm
        if event_obj.event_state == 0:
            found, to_be_cleared = cls.check_for_events_in_time_window(
                event_obj
            )
            if found:
                clears = []
                for e in to_be_cleared:
                    if not e.cleared_by:
                        e.cleared_by = event_obj.id
                        e.is_active = False
                        clears.append(e.id)
                        e.save()
                event_obj.cleared_alarms = "{}".format(clears)
                event_obj.save()
            assert event_obj.event_state == 0

        #  Detect if Service is flapping
        #  TODO: List all flapping services and recheck their flapping status.
        cls.detect_service_flapping(event_obj, server)

        process_event(event_obj)
        return event_obj

    @classmethod
    def check_for_events_in_time_window(cls, event_obj, threshold=86400):
        d = timedelta(seconds=threshold)
        now = event_obj.event_time
        lower_bound = now - d
        found = False

        events = cls.objects.filter(
            server=event_obj.server,
            service=event_obj.service,
            event_type=event_obj.event_type,
            event_id=event_obj.event_id,
            event_state=1,
            created_at__gte=lower_bound)

        found = events.exists()

        return found, events

    @classmethod
    def check_active_alarms(cls, event_obj, threshold=86400):
        utc = timezone('UTC')
        td = timedelta(seconds=threshold)
        utc_now = datetime.datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=utc)
        lower_bound = utc_now - td

        #  We received error alarm, we will check for old duplicates in the raised ones.
        #  Only check acknowledged alarms int he last period (configurable)
        events = cls.objects.filter(
            server=event_obj.server,
            service=event_obj.service,
            event_type=event_obj.event_type,
            event_id=event_obj.event_id,
            is_active=True,
            is_ack=False,
            event_time__gte=lower_bound
        )

        found = events.exists()
        return found, events

    @classmethod
    def update_server_running_status(cls, event_obj, server):

        monit_stopped_pattern = re.compile("^Monit.*stopped$|.*Host.*Down.*")
        server.server_up = True
        if not event_obj.externalevent:
            if event_obj.event_action == 3 and monit_stopped_pattern.match(event_obj.event_message):
                server.server_up = False
                event_obj.event_state = 1
        else:
            if event_obj.event_state == 1:
                server.server_up = False
                server.save()
        server.save()
        return event_obj

    @classmethod
    def detect_service_flapping(cls, evt, server):
        event_service = evt.service

        if int(evt.event_type) != 3:
            return
        try:
            server_tz = timezone("UTC")
            now = datetime.datetime.utcnow().replace(tzinfo=server_tz)

            # Between 0 and 86399 inclusive
            flapping_period = timedelta(
                seconds=settings.SERVICE_FLAPPING_PERIOD)
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

    def to_dict(self):
        event_dict = dict()
        event_dict["id"] = self.id
        event_dict["server_id"] = clean(self.server.id)
        event_dict["server"] = self.server.localhostname
        event_dict["service"] = self.service.name.replace(
            '___', '/').replace('__', '_').replace('_', '/')
        event_dict["message"] = self.event_message
        # Strings
        event_dict["state"] = event_status_to_string(self.event_id)
        event_dict["event"] = event_state_to_string(self.event_state)
        event_dict["action"] = action_to_string(self.event_action)
        event_dict["type"] = type_to_string(self.event_type)
        # Id
        event_dict["state_id"] = self.event_state
        event_dict["event_id"] = self.event_id
        event_dict["action_id"] = self.event_action
        event_dict["type_id"] = int(self.event_type)
        monit_stopped_pattern = re.compile("^Monit.*stopped$|.*Host.*Down.*")
        event_dict["server_down"] = False
        if self.event_action == 3 and monit_stopped_pattern.match(self.event_message):
            event_dict["server_down"] = True
        return event_dict

    def __str__(self):
        return json.dumps(self.to_dict())


class MonitEventComment(models.Model):
    event = models.ForeignKey(MonitEvent)
    user = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField()

    @classmethod
    def create(cls, user, event, comment):
        comment_obj = cls(
            event=event,
            user=user,
            content=comment
        )
        comment_obj.save()
        return comment_obj


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


def check_host_group_match(hg, host_groups_comma_seperated):
    '''
    This function checks if a host group (hg) matches the comma seperated list of
    masks.
    '''
    #  If we actually have a list
    if host_groups_comma_seperated:
        masks = host_groups_comma_seperated.split(',')
        for mask in masks:
            #  We check both slug and the display name
            if re.search(mask, hg.slug):
                return True
            if re.search(mask, hg.display_name):
                return True
        # The only case the function return False is when we don't find any
        # match !
        return False
    #  We return True if we don't have list
    return True


def check_server_name_match(server_name, server_names_comma_seperated):
    if server_names_comma_seperated:
        masks = server_names_comma_seperated.split(',')
        for mask in masks:
            if re.search(
                    mask, server_name):
                return True
        return False
    return True


def process_event(event_object):
    org = event_object.server.organisation
    server_name = event_object.server.localhostname
    hg = event_object.server.host_group

    mute_notifications = list()
    remaining_notifications = list()
    for nt in org.notificationtype_set.all():
        if "mute" in nt.notification_class.lower():
            #  These are mute rules
            mute_notifications.append(nt)
        else:
            #  The rest.
            remaining_notifications.append(nt)

    for nt in mute_notifications:
        if nt.notification_enabled:
            hg_matches = check_host_group_match(hg, nt.notification_host_group)
            server_matches = check_server_name_match(
                server_name, nt.notification_server)
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

            if name_matches and state_matches and action_matches and type_matches and messages_matches and hg_matches and server_matches:
                broadcast_muted_event_to_websocket_channel(event_object)
                MonitEvent.mute(event_object)

    if not event_object.is_ack:
        broadcast_event_to_websocket_channel(event_object)
        for nt in remaining_notifications:
            if nt.notification_enabled:
                hg_matches = check_host_group_match(
                    hg, nt.notification_host_group)
                server_matches = check_server_name_match(
                    server_name, nt.notification_server)
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

                if name_matches and state_matches and action_matches and type_matches and messages_matches and hg_matches and server_matches:
                    notification_handler_module = importlib.import_module(
                        "djangomonitcollector.notificationsystem.lib.{0}".format(nt.notification_class.lower()))
                    class_ = getattr(
                        notification_handler_module, nt.notification_class)
                    notification_class_instance = class_()
                    notification_class_instance.set_event(event_object)
                    notification_class_instance.set_extra_params(
                        nt.notification_plugin_extra_params)
                    notification_class_instance.set_notification_id(nt.id)

                    try:
                        output = notification_class_instance.process()
                        f = open(notification_class_instance.get_std_output(), 'a+')
                        f.write("{}".format(output))
                        f.close()
                    except StandardError as e:
                        f = open(notification_class_instance.get_err_output(), 'a+')
                        f.write("{}".format(e))
                        f.close()


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
    if event_type == 1:
        return Directory.get_by_name(server, service_name)
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


def broadcast_muted_event_to_websocket_channel(event_object):
    response = dict()
    response['channel'] = "organisation_muted_events_{0}".format(
        str(event_object.server.organisation.id).replace('-', '_'))
    response['event'] = event_object.to_dict()
    response_str = json.dumps(response)
    to_queue(response_str)


def broadcast_event_to_websocket_channel(event_object):
    response = dict()
    response['channel'] = "organisation_events_{0}".format(
        str(event_object.server.organisation.id).replace('-', '_'))
    response['event'] = event_object.to_dict()
    response_str = json.dumps(response)
    to_queue(response_str)
