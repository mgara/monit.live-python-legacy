# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import uuid

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class User(AbstractUser):
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    is_customer = models.BooleanField(blank=True, default=True)
    bootstrap_theme = models.CharField(max_length=20,default="paper")
    dygraph_color_palette = models.CharField(max_length=255,default='["#173e43", "#b56969", "#22264b", "#3fb0ac"]')

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})


def validate_user(user):
    if not user.id:
        return False
    if user.is_customer and user.is_active:
        return True
    return False


class CollectorKey(models.Model):
    collector_key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User)
    is_enabled = models.BooleanField(default=True)

    @classmethod
    def create(cls,
               uuid,
               user):
        entity = cls(collector_key=uuid, user_id=user, is_enabled=True)
        entity.save()
        return entity
