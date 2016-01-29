from django.db import models

class Service(models.Model):

    name = models.TextField()
    service_type = models.PositiveIntegerField(null=True)
    status = models.TextField(null=True)
    status_hint = models.IntegerField(null=True)
    monitor = models.IntegerField(null=True)
    monitor_mode = models.IntegerField(null=True)
    pending_action = models.IntegerField(null=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
