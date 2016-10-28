import json
import os
import ast

from abc import ABCMeta, abstractmethod
from djangomonitcollector.ui.templatetags.extra_tags \
    import event_status_to_string, \
    event_state_to_string, \
    action_to_string, \
    type_to_string


'''
This interface is the base class for the EventSettings
'''


class EventSettingsInterface(object):
    __metaclass__ = ABCMeta

    extra_params = dict()
    event = None
    notification_type = None
    has_extra_config = False

    PLUGIN_ERROR_OUTPUT = "{}/plugin_error_output/{}_err_log"
    PLUGIN_STD_OUTPUT = "{}/plugin_std_output/{}_std.log"
    PLUGIN_NAME = "PLUGIN_NAME"
    PLUGIN_ICON = "PLUGIN_ICON"
    HELP_MESSAGE = ""
    TOOLTIP = ""

    def set_notification_id(self, notificationid):
        self.PLUGIN_ERROR_OUTPUT = self.PLUGIN_ERROR_OUTPUT.format(os.getcwd(), notificationid)
        self.PLUGIN_STD_OUTPUT = self.PLUGIN_STD_OUTPUT.format(os.getcwd(), notificationid)

    def get_std_output(self):
        return self.PLUGIN_STD_OUTPUT

    def get_err_output(self):
        return self.PLUGIN_ERROR_OUTPUT

    def get_freindlyname(self):
        return self.PLUGIN_NAME

    def get_icon(self):
        return u"fa fa-{}".format(self.PLUGIN_ICON)

    def get_helpmessage(self):
        return self.HELP_MESSAGE

    def get_tooltip(self):
        return self.TOOLTIP

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
        self.event_service = self.event.service
        self.service_name = self.event_service.name.replace(
            '___', '/').replace('__', '_').replace('_', '/')
        self.event_message = self.event.event_message

        self.event_type_id = int(self.event.event_type)
        self.event_id_id = self.event.event_id
        self.event_action_id = self.event.event_action
        self.event_state_id = self.event.event_state

        self.event_type = type_to_string(self.event.event_type)
        self.event_action = action_to_string(self.event.event_action)
        self.event_state = event_state_to_string(self.event.event_state)
        self.event_id = event_status_to_string(self.event.event_id)

    def get_event_summary(self):
        event_dict = dict()
        event_dict["server"] = self.server
        event_dict["service"] = self.event_service.name
        event_dict["message"] = self.event_message
        # Strings
        event_dict["state"] = self.event_state
        event_dict["event"] = self.event_id
        event_dict["action"] = self.event_action
        event_dict["type"] = self.event_type
        # Id
        event_dict["state_id"] = self.event_state_id
        event_dict["event_id"] = self.event_id_id
        event_dict["action_id"] = self.event_action_id
        event_dict["type_id"] = self.event_type_id

        return json.dumps(event_dict, sort_keys=True, indent=4)

    def set_extra_params(self, extra_params):
        if extra_params:
            if len(extra_params) > 0:
                self.extra_params = ast.literal_eval(extra_params)
                return
        self.extra_params = None
