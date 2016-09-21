# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

import json
import os
import time
import urllib
import logging

from datetime import datetime
from httplib import HTTPConnection
from mako.template import Template
from optparse import make_option
from pytz import timezone
from urlparse import urlparse

FILENAME = '/var/log/kairos/monit_collector_host_heartbeat.log'
FORMAT = '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'


class Command(BaseCommand):
    help = 'This program will check the avaibility of monit hosts'
    option_list = BaseCommand.option_list + (
        make_option('--host', dest='host', default='localhost'),
        make_option('--port', dest='port',  default='5001'),
        make_option('--log', dest='log', default='INFO'),
        make_option("--verbose", action="store_true", dest="verbose"),
    )

    # create logger with 'spam_application'
    logger = logging.getLogger('monit_host_heartbeat')

    def handle(self, *args, **options):
        log_level = eval('logging.' + options['log'].upper())

        self.logger.setLevel(log_level)
        lh = logging.FileHandler(FILENAME)
        formatter = logging.Formatter(FORMAT)

        if options['verbose']:
            lh = logging.StreamHandler()
        lh.setLevel(log_level)
        lh.setFormatter(formatter)
        self.logger.addHandler(lh)

        utc_tz = timezone("UTC")
        servers_count = 0
        hosts_down = []
        self.logger.info("Started MonitHost HeartBeat")
        while True:
            time.sleep(10)
            monit_hosts = self.get_monit_hosts(options)
            if not monit_hosts:
                self.logger.info("No Hosts Found or No Hosts configured")
                continue
            for h in monit_hosts:
                servers_count += 1
                server = monit_hosts[h]

                server_monit_update_period = int(server['monit_update_period'])
                server_incarnation = datetime.strptime(server['incarnation'],
                                                       "%Y-%m-%dT%H:%M:%S.%fZ")
                server_incarnation = server_incarnation.replace(tzinfo=utc_tz)
                now = datetime.utcnow().replace(tzinfo=utc_tz)
                delta = (now - server_incarnation).seconds

                self.logger.debug("last data received for [{}] is [{}] seconds\
 ago, monit update period [{}] seconds  ".format(
                    server['localhostname'],
                    delta, server['monit_update_period'])
                )
                # TODO: make the grace period of 10 seconds configurable, 0 is aggressive
                if (delta - 10) > server_monit_update_period:

                    if server['monitid'] not in hosts_down:
                        hosts_down.append(server['monitid'])
                        self.logger.debug(
                            "Generating Host Down Alert {}".format(h))
                        self.host_went_down(server, delta, options)
                    else:
                        self.logger.debug(
                            "We Know about this host .... {}".format(h))
                else:
                    if server['monitid'] in hosts_down:
                        hosts_down.remove(server['monitid'])
                        self.host_is_up_again(server, options)
            time.sleep(10)

    def get_monit_hosts(self, options):
        try:
            endpoint = "http://{0}:{1}/dc/get_servers/".format(
                options['host'],
                options['port']
            )
            filehandle = urllib.urlopen(endpoint)
            json_response = filehandle.read()
            return json.loads(json_response)
        except IOError:
            self.logger.critical("Collector Is Down ?")
            return None

    def host_went_down(self, server, delta, options):
        data = self.get_event_post_data(
            monit_instance_id=server['monitid'],
            localhostname=server['localhostname'],
            collected_sec="{0}".format(time.time()).split(".")[0],
            collected_usec="0",
            event_type=4,
            event_id=4,
            event_state=1,
            event_action=1,
            event_message="Host timeout {0} last received data {1} seconds ago".format(
                server['localhostname'], delta)
        )
        options['org_id'] = server['org_id']
        options['host_group'] = server['host_group']
        self.post(options, data)

    def host_is_up_again(self, server, options):
        data = self.get_event_post_data(
            monit_instance_id=server['monitid'],
            localhostname=server['localhostname'],
            collected_sec="{0}".format(time.time()).split(".")[0],
            collected_usec="0",
            event_type=4,
            event_id=4,
            event_state=0,
            event_action=1,
            event_message="Server {0} is Back!".format(server['localhostname'])
        )
        options['org_id'] = server['org_id']
        options['host_group'] = server['host_group']
        self.post(options, data)

    def get_event_post_data(self,
                            monit_instance_id,
                            localhostname,
                            collected_sec,
                            collected_usec,
                            event_type,
                            event_id,
                            event_state,
                            event_action,
                            event_message,
                            ):

        template_directory = os.path.dirname(os.path.abspath(__file__))
        template_directory = os.path.join(template_directory, "templates")
        template_filename = os.path.join(
            template_directory, "event_template.tpl")
        template = Template(filename=template_filename)

        content = template.render(
            monit_instance_id=monit_instance_id,
            localhostname=localhostname,
            collected_sec=collected_sec,
            collected_usec=collected_usec,
            event_type=event_type,
            event_id=event_id,
            event_state=event_state,
            event_action=event_action,
            event_message=event_message
        )

        return content

    def post(self, options, data):
        if "host_group" in options:
            url = "http://{0}/dc/collector/{1}/{2}/".format(
                options['host'], options['org_id'], options["host_group"])
        else:
            url = "http://{0}/dc/collector/{1}/".format(
                options['host'], options['org_id'])
        urlparts = urlparse(url)
        conn = HTTPConnection(urlparts.netloc, int(options['port']))
        conn.request("POST", urlparts.path, data)
        resp = conn.getresponse()
        body = resp.read()
        self.logger.debug("Sent {} ".format(data))
