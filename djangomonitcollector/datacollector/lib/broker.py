import pika
from django.conf import settings


def to_queue(message):
    connection = None

    rabbitmq_resource = getattr(
        settings, 'BROKER_URL', 'amqp://dmc:va2root@172.16.5.83:5672/%2f')
    rabbitmq_queue = getattr(settings, 'RABBITMQ_QUEUE', 'dmc')
    parameters = pika.URLParameters(rabbitmq_resource)

    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(
        queue=rabbitmq_queue, durable=True, exclusive=False, auto_delete=False)

    # Enabled delivery confirmations
    channel.confirm_delivery()

    channel.basic_publish(exchange='dmc',
                          routing_key='dmc',
                          body=message)

    connection.close()
