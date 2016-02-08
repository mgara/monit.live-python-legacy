
from ieventnotification import IEventSettingsInterface
from parameter import Parameter


class EmailEventNotification(IEventSettingsInterface):

    extra_params = {
        'to': Parameter('to','To'),
        'subjet_prefix':Parameter('subjet_prefix','Subject Prefix'),
    }


    def __init__(self):
        pass

    def process(self):
        print self.event
        print self.extra_params

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass

