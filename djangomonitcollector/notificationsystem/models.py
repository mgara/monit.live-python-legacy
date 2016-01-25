from __future__ import unicode_literals, absolute_import

import datetime
from django.db import models
from pytz import timezone
from djangomonitcollector.datacollector.models.server import MonitEvent, Server
from djangomonitcollector.datacollector.models.service import Service
from djangomonitcollector.users.models import User

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

EVENT_STATUS_CHOICES = (
    (0,'-'),
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
    (9,'-'),
    (0,'Success'),
    (1,'Error'),
    (2,'Change'),
    (3,'Link mode not changed')
)

class NotificationType(models.Model):
    notification_user = models.ForeignKey(User)
    notification_service = models.ForeignKey(Service)
    notification_type = models.PositiveIntegerField(null=True,choices=EVENT_STATUS_CHOICES, default=0)
    notification_state = models.PositiveIntegerField(null=True,choices=EVENT_STATE_CHOICES, default=0)
    notification_action = models.PositiveIntegerField(null=True)
    notification_message = models.TextField(null=True)
    notification_class = models.CharField(max_length=32)



class Notification(models.Model):
    notification_user = models.ForeignKey(User)
    notification_type = models.ForeignKey(NotificationType)
    notification_event = models.ForeignKey(MonitEvent)

    @classmethod
    def create(cls,
               notification_class,
               notification_event
               ):
        notification_obj = cls(
            notification_class=notification_class,
            notification_event=notification_event
        )
        notification_obj.save()
        return notification_obj



