__author__ = 'mehergara'
from ieventnotification import IEventSettingsInterface
from djangomonitcollector.datacollector.models.server import MonitEvent


class MuteEventNotification(IEventSettingsInterface):


    def process(self):
        MonitEvent.mute(self.event)

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass

