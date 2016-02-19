import factory
from ..models import Server


class ServerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Server
