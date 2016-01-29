from django import forms
from models import NotificationType
from djangomonitcollector.datacollector.models.service import Service
from os import listdir
from os.path import isfile, join
import os

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

def get_classes():
    excluded_classes = ['__init__.py','ieventnotification.py']
    classes_path = "{0}/djangomonitcollector/notificationsystem/lib/".format(os.getcwd())
    classes_tuple = list()
    classes_list = [f for f in listdir(classes_path) if isfile(join(classes_path, f))]
    filtered_classes = [x for x in classes_list if x not in excluded_classes]

    for path in filtered_classes :
        class_name = path.split(".")[0]
        e = (class_name,class_name.upper())
        classes_tuple.append(e)
    return tuple(classes_tuple)

class NotificationTypeForm(forms.ModelForm):

    notification_service = forms.ModelMultipleChoiceField(Service.objects.all(), required=False)
    notification_type = forms.MultipleChoiceField(choices=EVENT_STATUS_CHOICES, required=False)
    notification_action = forms.MultipleChoiceField(choices=EVENT_ACTION_CHOICES, required=False)
    notification_state = forms.MultipleChoiceField(choices=EVENT_STATE_CHOICES, required=False)
    notification_class = forms.MultipleChoiceField(choices=get_classes(), required=True)

    class Meta:
        model = NotificationType
        fields =[
            'notification_user',
            'notification_message',
            'notification_service',
            'notification_type',
            'notification_action',
            'notification_state',
            'notification_class'
        ]

    def save(self, force_insert=False, force_update=False, commit=True):
        nt = super(NotificationTypeForm, self).save(commit=False)
        if commit:
            nt.save()
        return nt




