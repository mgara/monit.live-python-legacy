#!/usr/bin/env python
import json
import flask
import gevent
import logging
import requests
import kombu.mixins
from kombu import Exchange
import os
from optparse import OptionParser, OptionGroup

from gevent import monkey
from flask_socketio import SocketIO, emit, disconnect


app = flask.Flask(__name__,
                  template_folder='/templates',
                  )

app.config['SECRET_KEY'] = os.getenv('APP_SECRET')

socketio = SocketIO(app)


FILENAME = '../logs/kairos_io.log'
FORMAT = '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'


@app.route('/<path:url>', methods=['GET', 'POST', 'DELETE'])
def route(url):
    global logger

    if flask.request.method == 'GET':
        req = requests.get(url, stream=True)
        logger.debug('HTTP GET [{}] '.format(url))

    if flask.request.method == 'POST':
        req = requests.post(url, data=json.dumps(flask.request.json),
                            headers={'content-type': 'application/json'},
                            stream=True)
        logger.debug('HTTP POST [{}] '.format(url))

    if flask.request.method == 'DELETE':
        req = requests.delete(url, stream=True)

    return flask.Response(flask.stream_with_context(req.iter_content()),
                          content_type=req.headers['content-type'])


@socketio.on('disconnect request', namespace='/dmc')
def disconnect_request():
    emit('dmc', {'data': {'event_type': 'disconnected'}})
    disconnect()


@socketio.on('connect', namespace='/dmc')
def test_connect():
    global logger
    logger.info('client [{}] connected'.format(flask.request.sid))
    emit('dmc', {'data': {'event_type': 'connected'}})


@socketio.on('disconnected', namespace='/dmc')
def test_disconnect():
    global logger
    logger.info('client [{}] disconnected'.format(flask.request.sid))


class Broker(kombu.mixins.ConsumerMixin):

    def __init__(self):
        super(Broker, self).__init__()
        global BROKER_URL
        broker_url = BROKER_URL
        global logger
        logger.info('Broker Started on: {}'.format(broker_url))
        self.connection = kombu.Connection(
            broker_url)

    def on_message(self, body, message):
        try:

            global logger

            body = body.encode('ascii', 'ignore')
            logger.debug('Received: {}'.format(body))
            if isinstance(body, str):
                data = json.loads(body)
                channel = data.get('channel')
            namespace = '/{}'.format(channel)

            socketio.emit('dmc', {'data': data},
                          namespace=namespace,
                          broadcast=True)

            message.ack()

        except Exception as e:
            logging.exception(e)
            message.reject()

    def get_consumers(self, consumer, channel):
        exchange = Exchange('dmc', type='topic')

        queue = kombu.Queue(
            'dmc',
            exchange=exchange,
            routing_key='dmc')

        return [consumer([queue],
                         callbacks=[self.on_message],
                         auto_declare=False)]


def run(host, port):
    monkey.patch_all()
    gevent.spawn(Broker().run)
    socketio.run(app, host=host, port=port)


if __name__ == "__main__":

    parser = OptionParser()
    group = OptionGroup(parser, "Required Options")

    group.add_option(
        "-B",
        "--broker_url",
        dest="broker_url",
        help="RabbitMQ Url",
        metavar="BROKER_URL"
    )

    group.add_option(
        "-H",
        "--host",
        dest="host",
        help="Websocket IO Binding Address",
        metavar="HOST"
    )

    group.add_option(
        "-P",
        "--port",
        dest="port",
        type=int,
        help="Websocket IO Binding port",
        metavar="PORT"
    )
    parser.add_option_group(group)

    group = OptionGroup(parser, "Debug Options")

    group.add_option(
        "-l",
        "--log_level",
        dest="log",
        help="Application Log Level (Default : INFO) ",
        metavar="LOG_LEVEL",
        default='INFO'
    )

    group.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="don't print status messages to stdout"
    )
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
    #  create logger with 'spam_application'
    global logger
    logger = logging.getLogger('kairos.io')

    log_level = eval('logging.' + options.log.upper())

    logger.setLevel(log_level)
    lh = logging.FileHandler(FILENAME)
    formatter = logging.Formatter(FORMAT)

    if options.verbose:
        lh = logging.StreamHandler()
    lh.setLevel(log_level)
    lh.setFormatter(formatter)
    logger.addHandler(lh)

    logger.info("Started Monit Collector IO")
    host = options.host
    port = options.port

    global BROKER_URL
    BROKER_URL = options.broker_url
    run(host, port)
