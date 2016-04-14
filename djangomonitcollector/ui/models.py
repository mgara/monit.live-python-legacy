import logging
import hashlib
import random

from django.db import models
from django.utils.translation import ugettext_lazy as _

from djangomonitcollector.users.models import Organisation

#  Get an instance of a logger
logger = logging.getLogger(__name__)


class HostGroup(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    slug = models.CharField(max_length=40)
    owned_by = models.ForeignKey(Organisation)
    display_name = models.CharField(_("Display Name"), max_length=40, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def update(cls, org, slug):
        host_group, created = HostGroup.objects.get_or_create(
            slug=slug, owned_by=org, display_name=slug.title())
        return host_group, created

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()

        super(HostGroup, self).save(*args, **kwargs)
