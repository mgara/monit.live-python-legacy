from abc import ABCMeta, abstractmethod
import ast
from djangomonitcollector.ui.templatetags.extra_tags \
    import event_status_to_string, \
    event_state_to_string, \
    action_to_string,\
    type_to_string

'''
This interface is the base class for the EventSettings
'''


class IEventSettingsInterface(object):
    __metaclass__ = ABCMeta

    extra_params = dict()
    event = None
    notification_type = None

    '''
    this function takes as a parametr the event object and will 
    indicate how to process the event
    '''

    @abstractmethod
    def process(self, event_object):
        raise

    '''
    this function will be called when the process is done
    '''

    @abstractmethod
    def finalize(self, event_object):
        pass

    def set_event(self, event_object):
        self.event = event_object
        self.server = self.event.server.localhostname
        self.event_message = self.event.event_message
        self.event_type = type_to_string(self.event.event_type)
        self.event_action = action_to_string(self.event.event_action)
        self.event_service = self.event.service
        self.event_state = event_state_to_string(self.event.event_state)
        self.event_status = event_status_to_string(self.event.event_id)

    def get_event_summary(self):
        return "Server:\t{4} \nStatus:\t[{0}] \nState:\t[{1}] \nService:\
\t[{2}] \nType:\t{5} \nMessage:\t[{3}] ".format(
            self.event_status,
            self.event_state,
            self.event_service,
            self.event_message,
            self.server,
            self.event_type
            )

    def set_extra_params(self, extra_params):
        if extra_params:
            if len(extra_params) > 0:
                self.extra_params = ast.literal_eval(extra_params)
                return
        self.extra_params = None
