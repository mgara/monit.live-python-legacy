from djangomonitcollector.datacollector.models.server import MonitEvent
from ieventnotification import EventSettingsInterface


class MuteEventNotification(EventSettingsInterface):

    PLUGIN_NAME = "Mute Event"
    PLUGIN_ICON = "times-circle"

    def process(self):
        MonitEvent.mute(self.event)

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass
