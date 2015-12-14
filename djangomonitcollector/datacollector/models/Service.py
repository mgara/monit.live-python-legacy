from django.db import models


# Service
class Service(models.Model):
    # not unique since there could be multiple server with service 'nginx', etc.
    name = models.TextField()
    status = models.TextField(null=True)
    status_hint = models.IntegerField(null=True)
    monitor = models.IntegerField(null=True)
    monitor_mode = models.IntegerField(null=True)
    pending_action = models.IntegerField(null=True)
