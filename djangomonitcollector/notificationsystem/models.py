from __future__ import unicode_literals, absolute_import

import hashlib
import logging
import random

from django.core.urlresolvers import reverse
from django.db import models

from djangomonitcollector.users.models import User, Organisation

# Get an instance of a logger
logger = logging.getLogger(__name__)


class NotificationType(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    notification_user = models.ForeignKey(User)
    organisation = models.ForeignKey(Organisation)

    notification_server = models.CharField(null=True, max_length=255)
    notification_host_group = models.CharField(null=True, max_length=255)
    notification_service = models.CharField(null=True, max_length=255)
    notification_type = models.CharField(null=True, max_length=255)
    notification_state = models.CharField(null=True, max_length=255)
    notification_action = models.CharField(null=True, max_length=255)
    notification_message = models.CharField(null=True, max_length=255)
    notification_class = models.CharField(max_length=50)

    notification_label = models.CharField(max_length=100)
    notification_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    notification_plugin_extra_params = models.TextField(null=True)

    def get_absolute_url(self):
        return reverse('n:notificationtype_view', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()

        super(NotificationType, self).save(*args, **kwargs)

