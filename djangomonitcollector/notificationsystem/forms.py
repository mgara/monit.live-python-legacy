import importlib
import json
import os
from os import listdir
from os.path import isfile, join

from django import forms
from django.utils.translation import ugettext as _

from models import NotificationType

EVENT_STATUS_CHOICES = (
    (1, 'checksum'),
    (2, 'resource'),
    (4, 'timeout'),
    (8, 'timestamp'),
    (16, 'size'),
    (32, 'connection'),
    (64, 'permission'),
    (128, 'UID'),
    (256, 'GID'),
    (512, 'nonexist'),
    (1024, 'invalid'),
    (2048, 'data'),
    (4096, 'exec'),
    (8192, 'fsflags'),
    (16384, 'icmp'),
    (32768, 'content'),
    (65536, 'instance'),
    (131072, 'action'),
    (262144, 'PID'),
    (524288, 'PPID'),
    (1048576, 'heartbeat'),
    (2097152, 'status'),
    (4194304, 'uptime'),
    (16777216, 'link mode/speed'),

)

EVENT_STATE_CHOICES = (
    (0, 'Success'),
    (1, 'Error'),
    (2, 'Change'),
    (3, 'Link mode not changed'),
    (4, 'Host Down')
)
EVENT_ACTION_CHOICES = (
    (1, 'Alert (monit alert generated)'),
    (2, 'Restart (trying to restart)'),
    (3, 'Stop'),
    (4, 'Exec'),
    (5, 'Unmonitor'),
    (6, 'Reload'),
)

'''
Check if file is valid : is an actual file and its name doesn't match the pattern (Exclusion list)
'''
def validate_file(classes_path, f):
    excluded_files = (
        '__init__.py', 'ieventnotification.py', 'parameter.py', '.pyc')
    if isfile(join(classes_path, f)):
        for excluded_pattern in excluded_files:
            if excluded_pattern in f:
                return False
        return True
    return False


'''
Get the class name and the extra parameters field
'''
def get_class_name_and_extra_params(classname):
    # TODO: read the module from settings ?
    notification_handler_module = importlib.import_module(
        "djangomonitcollector.notificationsystem.lib.{0}".format(classname))
    module_attrs = notification_handler_module.__dict__
    for k in module_attrs.keys():
        if k.lower() == classname:
            return k, module_attrs[k].extra_params



'''
Return a tuple that contains the class name and the actual name that we want to display in the form
'''
def get_notification_plugins_classes():
    classes_list = get_notification_plugins()
    classes_tuple = list()
    for path in classes_list:
        class_name = path.split(".")[0]
        class_name, extra_attr = get_class_name_and_extra_params(class_name)
        e = (class_name, class_name)
        classes_tuple.append(e)
    return tuple(classes_tuple)


def get_notification_plugins():
    classes_path = "{0}/djangomonitcollector/notificationsystem/lib/".format(
        os.getcwd())
    classes_list = [
        f for f in listdir(classes_path) if validate_file(classes_path, f)]
    return classes_list


class NotificationTypeForm(forms.ModelForm):
    notification_service = forms.CharField(required=False)

    notification_host_group = forms.CharField(
        required=False,
        help_text=_('Tags, Apply notification to this list of host groups (wildcards are permitted)')
        )

    notification_server = forms.CharField(
        required=False,
        help_text=_('Tags, Apply notification to this list of servers (wildcards are permitted)')
        )

    notification_type = forms.MultipleChoiceField(
        choices=EVENT_STATUS_CHOICES, required=False)
    notification_action = forms.MultipleChoiceField(
        choices=EVENT_ACTION_CHOICES, required=False)
    notification_state = forms.MultipleChoiceField(
        choices=EVENT_STATE_CHOICES, required=False)
    notification_class = forms.ChoiceField(
        choices=get_notification_plugins_classes(), required=True)

    class Meta:
        model = NotificationType
        fields = [
            'notification_host_group',
            'notification_server',
            'notification_label',
            'notification_enabled',
            'notification_message',
            'notification_service',
            'notification_type',
            'notification_action',
            'notification_state',
            'notification_class',
        ]

    def null_or_empty(self, item, data_dict):
        if item in data_dict:
            if data_dict[item][0]:
                return False
        return True

    def save(self, force_insert=False, force_update=False, commit=True):

        nt = super(NotificationTypeForm, self).save(commit=False)
        data_dict = dict(self.data.iterlists())

        if 'notification_service' in data_dict:
            notification_services = data_dict['notification_service']
            service_array = json.dumps(notification_services)
            nt.notification_service = service_array
        else:
            nt.notification_service = ""

        if 'notification_type' not in data_dict:
            nt.notification_type = ""

        if 'notification_action' not in data_dict:
            nt.notification_action = ""

        if 'notification_state' not in data_dict:
            nt.notification_state = ""

        if self.null_or_empty('notification_host_group', data_dict):
            nt.notification_host_group = ""

        if self.null_or_empty('notification_server', data_dict):
            nt.notification_server = ""

        notification_class = self.cleaned_data['notification_class']
        k, plugin_fields = get_class_name_and_extra_params(
            notification_class.lower())
        notification_extra_params_dict = dict()
        for plugin_field in plugin_fields:
            notification_extra_params_dict[
                plugin_field] = self.data[plugin_field]

        nt.notification_plugin_extra_params = json.dumps(
            notification_extra_params_dict,
            sort_keys=True
        )

        if commit:
            nt.save()
        return nt
