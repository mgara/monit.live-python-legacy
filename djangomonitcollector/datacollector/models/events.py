
from django.db import models
import hashlib
import random
import uuid

from djangomonitcollector.users.models import Organisation


class EventStatusId(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_value = models.IntegerField()
    status_string = models.CharField(max_length=30)
    organisation = models.ForeignKey(Organisation)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        super(EventStatusId, self).save(*args, **kwargs)


class EventState(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_value = models.IntegerField()
    status_string = models.CharField(max_length=30)
    organisation = models.ForeignKey(Organisation)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        super(EventState, self).save(*args, **kwargs)


class EventAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_value = models.IntegerField()
    action_string = models.CharField(max_length=30)
    organisation = models.ForeignKey(Organisation)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        super(EventAction, self).save(*args, **kwargs)


class EventServiceType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_value = models.IntegerField()
    type_string = models.CharField(max_length=30)
    organisation = models.ForeignKey(Organisation)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        super(EventServiceType, self).save(*args, **kwargs)
