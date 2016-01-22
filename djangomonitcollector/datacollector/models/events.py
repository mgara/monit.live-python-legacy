from django.db import models
from pytz import timezone


class EventSettings(models.Model):
    setting = models.CharField(size=40)
    # this has to be a class that implements EventSetting Interface
    # with method Process
    # and Finalize
    #
    event_class = models.CharField(size=60)
