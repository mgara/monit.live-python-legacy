from django.db import models

from ..lib.utils import get_value


class Platform(models.Model):
    server = models.OneToOneField('Server')
    name = models.TextField(null=True)
    release = models.TextField(null=True)
    version = models.TextField(null=True)
    machine = models.TextField(null=True)
    cpu = models.IntegerField(null=True)
    memory = models.IntegerField(null=True)
    swap = models.IntegerField(null=True)

    @classmethod
    def update(cls, xmldoc, server):
        platform, created = Platform.objects.get_or_create(server=server)
        platform.name = get_value(xmldoc, "platform", "name")
        platform.release = get_value(xmldoc, "platform", "release")
        platform.version = get_value(xmldoc, "platform", "version")
        platform.machine = get_value(xmldoc, "platform", "machine")
        platform.cpu = get_value(xmldoc, "platform", "cpu")
        platform.memory = get_value(xmldoc, "platform", "memory")
        platform.swap = get_value(xmldoc, "platform", "swap")
        platform.save()
        return platform

    @classmethod
    def get_by_name(cls, server):
        service = cls.objects.get(server=server)
        return service


    def __str__(self):
        return 'a'
    def __unicode__(self):
        return u'a'
    def __repr__(self):
        return 'a'
