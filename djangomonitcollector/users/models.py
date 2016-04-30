# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import hashlib
import random
import uuid
import socket

from django import forms
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from djangomonitcollector.datacollector.lib.utils import TIMEZONES_CHOICES

from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import get_user_model



class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False


    def clean_email(self, email):
        """
        Validates an email value. You can hook into this if you want to
        (dynamically) restrict what email addresses can be chosen.
        """
        if not email.endswith("@vantrix.com"):
            raise forms.ValidationError("Must be a vantrix address")
        return email

    def new_user(self, request):
        """
        Instantiates a new User instance.
        """
        user = get_user_model()()
        #user.is_active = False
        return user


class Organisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, max_length=100, default="Default")
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organisation:view', kwargs={'id': self.id})

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


INSPINIA_SKINS = (
    ('-', 'default'),
    ('skin-1', 'Azure'),
    ('skin-2', 'Navy Blue'),
    ('skin-3', 'Sahara'),
)


@python_2_unicode_compatible
class User(AbstractUser):
    id = models.CharField(primary_key=True, max_length=40)
    organisation = models.ForeignKey(Organisation)
    organisation_manager = models.BooleanField(default=False)

    inspinia_skin = models.CharField(
        _("Application Skin"),
        choices=INSPINIA_SKINS,
        default='default',
        max_length=10
        )
    user_timezone = models.CharField(
        max_length=30, choices=TIMEZONES_CHOICES, default="Canada/Eastern")

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


def validate_user(user):
    if not user.id:
        return False
    if user.is_active:
        return True
    return False


class CollectorKey(models.Model):
    collector_key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

LOGGING_LEVEL = (
    ('info', 'Info'),
    ('warning', 'Warning'),
    ('error', 'Error'),
    ('critical', 'Critical'),
    ('debug', 'Debug'),
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
        _('Default server\'s TimeZone'), max_length=40, default="UTC", null=True)

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

    #  RabbitMQ/SocketIO
    rabbit_mq_enable_socket_io = models.BooleanField(
        _('Enable Live Data'),
        default=False
        )

    rabbit_mq_broker_url = models.CharField(
        _('Rabbit MQ Broker URL'),
        max_length=255,
        blank=True,
        null=True
        )

    #  Logging
    loggin_level = models.CharField(
        _('Logging Level'),
        max_length=10,
        choices=LOGGING_LEVEL,
        default='debug'
        )

    logging_logging_file = models.CharField(
        _('Logging File'),
        max_length=100,
        default="/var/log/vantrix/{}/monit_collector.log".format(socket.gethostname())
    )

    logging_enable_rsyslog = models.BooleanField(
        _('Enable Rsyslog'), default=False)
    logging_rsyslog_server = models.CharField(
        _('Rsyslog Server'), max_length=40, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def update(cls, organisation):
        settings, created = cls.objects.get_or_create(organisation=organisation)
        if not settings.id:
            settings.id = hashlib.sha1(str(random.random())).hexdigest()
            settings.save()
