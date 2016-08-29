# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import hashlib
import random
import uuid

from django import forms
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import get_user_model

from djangomonitcollector.datacollector.lib.utils import TIMEZONES_CHOICES


class MyAccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request):
        return True

    def clean_email(self, email):
        """
        Validates an email value. You can hook into this if you want to
        (dynamically) restrict what email addresses can be chosen.
        """
        #  if not email.endswith("@vantrix.com"):
        #      raise forms.ValidationError("Must be a vantrix address")
        return email

    def new_user(self, request):
        """
        Instantiates a new User instance.
        """
        user = get_user_model()()
        #  user.is_active = False
        return user


class OrganisationPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    permission = models.CharField(_('Permission'), max_length=40)

    def __str__(self):
        return self.permission

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        super(OrganisationPermission, self).save(*args, **kwargs)


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        _('Organisation Name'), null=True, max_length=100, default="Default")
    is_active = models.BooleanField(_('Is Active'), default=True)
    permissions = models.ManyToManyField(OrganisationPermission)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('datacollector:update_organisation', kwargs={'pk': self.id})

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        Settings.update(self)
        super(Organisation, self).save(*args, **kwargs)

    @classmethod
    def getdefault(cls):
        org, created = cls.objects.get_or_create(name="default")
        return org


admin.site.register(Organisation)
admin.site.register(OrganisationPermission)


class HostGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.CharField(max_length=40)
    owned_by = models.ForeignKey(Organisation)
    display_name = models.CharField(
        _("Display Name"), max_length=40, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def update(cls, org, slug):
        host_group, created = HostGroup.objects.get_or_create(
            slug=slug, owned_by=org, display_name=slug.title())
        return host_group, created

    def __str__(self):
        if self.display_name:
            return self.display_name
        return self.slug.title().replace("_", " ").replace("-", " ")

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        super(HostGroup, self).save(*args, **kwargs)


@python_2_unicode_compatible
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(Organisation)
    organisation_manager = models.BooleanField(
        _('Is Organisation Manager'), default=False)
    host_groups = models.ManyToManyField(HostGroup)

    user_timezone = models.CharField(
        _('User TimeZone'),
        max_length=30,
        choices=TIMEZONES_CHOICES,
        default="Canada/Eastern"
    )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def save(self, *args, **kwargs):

        try:
            assert self.organisation
        except:
            self.organisation = Organisation.getdefault()

        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        super(User, self).save(*args, **kwargs)


class UserSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    key = models.CharField(max_length=40)
    val = models.CharField(max_length=40)

    def save(self, *args, **kwargs):

        if not self.id:
            self.id = hashlib.sha1(str(random.random())).hexdigest()
            self.save(force_insert=True)
        super(UserSettings, self).save(*args, **kwargs)


def validate_user(user):
    if not user.id:
        return False
    if user.is_active:
        return True
    return False


class CollectorKey(models.Model):
    collector_key = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(Organisation)
    is_enabled = models.BooleanField(default=True)

    @classmethod
    def create(cls,
               uuid,
               org):
        entity = cls(collector_key=uuid, organisation=org, is_enabled=True)
        entity.save()
        return entity


SNMP_VERSIONS = (
    (1, 'version 1'),
    (2, 'version 2'),
    (3, 'version 3'),
)

SECURITY_PROTOCOL = (
    ('None', 'None'),
    ('SSL', 'SSL'),
    ('TLS', 'TLS'),
)


class Settings(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    organisation = models.OneToOneField(Organisation)

    #  General
    general_auto_add_unknown_servers = models.BooleanField(
        _('Auto accept new servers'), default=True)
    general_default_timezone_for_servers = models.CharField(
        _('Default server\'s TimeZone'),
        max_length=40,
        default="UTC",
        null=True
    )

    #  Flapping
    flapping_threshold = models.IntegerField(default=5)
    flapping_time_window = models.IntegerField(default=3600)

    #  SNMP Config
    snmp_version = models.IntegerField(
        choices=SNMP_VERSIONS,
        default=2)

    snmp_managers = models.CharField(
        max_length=200,
        default=None,
        null=True
    )

    email_smtp_server = models.CharField(
        _('SMTP Server'),
        max_length=255,
        null=True
    )

    email_smtp_port = models.IntegerField(
        _('Port'),
        default=25
    )

    email_use_ssl = models.CharField(
        max_length=5,
        choices=SECURITY_PROTOCOL,
        default="None"
    )

    email_sender_email = models.EmailField(
        _('Send from'),
        null=True
    )

    email_settings_authentication = models.BooleanField(
        _('Authentication'),
        default=False,
        blank=True
    )

    email_login = models.CharField(
        _('Login'),
        max_length=255,
        blank=True,
        null=True
    )

    email_password = models.CharField(
        _('Password'),
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def update(cls, organisation):
        settings, created = cls.objects.get_or_create(
            organisation=organisation)
        if not settings.id:
            settings.id = hashlib.sha1(str(random.random())).hexdigest()
            settings.save()
