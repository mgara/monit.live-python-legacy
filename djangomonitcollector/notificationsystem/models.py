from __future__ import unicode_literals, absolute_import

from django.db import models
from djangomonitcollector.datacollector.models.server import MonitEvent
from djangomonitcollector.users.models import User
from django.core.urlresolvers import reverse

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class NotificationType(models.Model):
    notification_user = models.ForeignKey(User)
    notification_service = models.CharField(null=True, max_length=255)
    notification_type = models.CharField(null=True, max_length=255)
    notification_state = models.CharField(null=True, max_length=255)
    notification_action = models.CharField(null=True, max_length=255)
    notification_message = models.CharField(null=True, max_length=255)
    notification_class = models.CharField(max_length=32)

    notification_label = models.CharField(max_length=100)
    notification_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    notification_plugin_extra_params = models.TextField(null=True)

    def get_absolute_url(self):
        return reverse('n:notificationtype_view', kwargs={'pk': self.pk})


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



