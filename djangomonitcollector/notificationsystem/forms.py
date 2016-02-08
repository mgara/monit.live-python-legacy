from django import forms
from models import NotificationType
from djangomonitcollector.datacollector.models.service import Service
from os import listdir
from os.path import isfile, join
import os
import json
import importlib

EVENT_STATUS_CHOICES = (
    (1,'checksum'),
    (2,'resource'),
    (4,'timeout'),
    (8,'timestamp'),
    (16,'size'),
    (32,'connection'),
    (64,'permission'),
    (128,'UID'),
    (256,'GID'),
    (512,'nonexist'),
    (1024,'invalid'),
    (2048,'data'),
    (4096,'exec'),
    (8192,'fsflags'),
    (16384,'icmp'),
    (32768,'content'),
    (65536,'instance'),
    (131072,'action'),
    (262144,'PID'),
    (524288,'PPID'),
    (1048576,'heartbeat'),
    (16777216,'link mode/speed'),
    (2097152,'status'),
    (4194304,'uptime')
)

EVENT_STATE_CHOICES = (
    (0,'Success'),
    (1,'Error'),
    (2,'Change'),
    (3,'Link mode not changed')
)
EVENT_ACTION_CHOICES = (
    (0,'0'),
    (1,'1'),
    (2,'2'),
    (3,'3'),
    (4,'4'),
    (5,'5'),
    (6,'6'),
)
'''
Check if file is valid : is an actual file and its name doesn't match the pattern (Exclusion list)
'''
def validate_file(classes_path,f):
    excluded_files = ('__init__.py','ieventnotification.py','parameter.py','.pyc')
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
    notification_handler_module = importlib.import_module("djangomonitcollector.notificationsystem.lib.{0}".format(classname))
    module_attrs= notification_handler_module.__dict__
    for k in module_attrs.keys():
        if k.lower() == classname:
            return k, module_attrs[k].extra_params


'''
Return a tuple that contains the class name and the actual name that we want to display in the form
'''
def get_notification_plugins_classes():
    classes_list = get_notification_plugins()
    classes_tuple = list()
    for path in classes_list :
        class_name = path.split(".")[0]
        class_name, extra_attr =get_class_name_and_extra_params(class_name)
        e = (class_name,class_name)
        classes_tuple.append(e)
    return tuple(classes_tuple)


def get_notification_plugins():
    classes_path = "{0}/djangomonitcollector/notificationsystem/lib/".format(os.getcwd())
    classes_list = [f for f in listdir(classes_path) if validate_file(classes_path, f)]
    return classes_list


class NotificationTypeForm(forms.ModelForm):

    notification_service = forms.ModelMultipleChoiceField(Service.objects.all(), required=False)
    notification_type = forms.MultipleChoiceField(choices=EVENT_STATUS_CHOICES, required=False)
    notification_action = forms.MultipleChoiceField(choices=EVENT_ACTION_CHOICES, required=False)
    notification_state = forms.MultipleChoiceField(choices=EVENT_STATE_CHOICES, required=False)
    notification_class = forms.ChoiceField(choices=get_notification_plugins_classes(), required=True)

    class Meta:
        model = NotificationType
        fields =[
            'notification_label',
            'notification_enabled',
            #TODO: must find a better way to get the current user.
            'notification_user',
            'notification_message',
            'notification_service',
            'notification_type',
            'notification_action',
            'notification_state',
            'notification_class',
        ]

    def save(self, force_insert=False, force_update=False, commit=True):
        nt = super(NotificationTypeForm, self).save(commit=False)

        service_array = json.dumps([ service.name for service in self.cleaned_data['notification_service'] ])
        notification_class= self.cleaned_data['notification_class']
        k,plugin_fields = get_class_name_and_extra_params(notification_class.lower())
        notification_extra_params_dict =dict()
        for plugin_field in plugin_fields:
            notification_extra_params_dict[plugin_field] = self.data[plugin_field]

        nt.notification_plugin_extra_params = json.dumps(
            notification_extra_params_dict,
            sort_keys=True
        )

        nt.notification_service = service_array
        if commit:
            nt.save()
        return nt




