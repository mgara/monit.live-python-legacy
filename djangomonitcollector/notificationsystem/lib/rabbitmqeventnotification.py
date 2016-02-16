__author__ = 'mehergara'
from ieventnotification import IEventSettingsInterface
from parameter import Parameter


class RabbitMQEventNotification(IEventSettingsInterface):
    extra_params = {
        'rabbitmq_server': Parameter('rabbitmq_server', 'Rabbit MQ Server'),
        'rabbitmq_routing_key': Parameter('rabbitmq_routing_key', 'Rabbit MQ Raouting Key'),
    }

    def process(self):
        pass

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass
