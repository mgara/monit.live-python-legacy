from ieventnotification import EventSettingsInterface
from parameter import Parameter

#  To be determined by the snmp standards
SEVERITY = (
    (10, "Info"),
    (11, "Critical"),
)


class OverrideSeverityEventNotification(EventSettingsInterface):

    PLUGIN_NAME = "Override Severity"
    PLUGIN_ICON = "random"

    extra_params = {
        'severity': Parameter('severity', 'New Severity', '', SEVERITY),
    }

    def process(self):
        self.event.event_state = self.extra_params["severity"]
        self.event.save()

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass
