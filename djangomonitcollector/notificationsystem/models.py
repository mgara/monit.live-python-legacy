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

class NotificationType(models.Model):
    notification_user = models.ForeignKey(User)
    notification_service = models.ForeignKey(Service)
    notification_type = models.PositiveIntegerField(null=True)
    notification_state = models.PositiveIntegerField(null=True)
    notification_action = models.PositiveIntegerField(null=True)
    notification_message = models.TextField(null=True)
    notification_class = models.CharField(max_length=32)


class Notification(models.Model):
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


