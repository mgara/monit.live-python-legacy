__author__ = 'mehergara'

from ieventnotification import IEventSettingsInterface
from parameter import Parameter


class SnmpEventNotification(IEventSettingsInterface):

    extra_params = {
        'snmp_managers': Parameter('snmp_managers','SNMP Managers List (comma seperated)'),
    }

    def __init__(self):
            pass

    def process(self):
        print self.event
        print self.extra_params

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass

