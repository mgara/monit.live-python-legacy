from __future__ import unicode_literals, absolute_import

from django.db import models


class Service(models.Model):
    name = models.TextField()
    service_group = models.IntegerField(null=True)
    service_type = models.PositiveIntegerField(null=True)
    status = models.TextField(null=True)
    status_hint = models.IntegerField(null=True)
    monitor = models.IntegerField(null=True)
    monitor_mode = models.IntegerField(null=True)
    pending_action = models.IntegerField(null=True)
    is_flapping = models.BooleanField(default=False)
    process_running_status = models.BooleanField(default=False)

    def __str__(self):
        return self.name.replace("___", "__").replace("__", "_").replace("_", "/").title()

    def __unicode__(self):
        return self.name.replace("___", "__").replace("__", "_").replace("_", "/").title()
