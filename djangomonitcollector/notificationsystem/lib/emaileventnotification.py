from django.core.mail import send_mail

from ieventnotification import EventSettingsInterface
from parameter import Parameter


class EmailEventNotification(EventSettingsInterface):
    extra_params = {
        'to': Parameter('to', 'To'),
        'subjet_prefix': Parameter('subjet_prefix', 'Subject Prefix'),
    }

    PLUGIN_NAME = "Email Notification"
    PLUGIN_ICON = "envelope"

    def __init__(self):
        pass

    def process(self):
        subjet_prefix = self.extra_params['subjet_prefix']
        to = self.extra_params['to']
        subject = "{0}:[{1}] on [{4}/{2}] action [{3}]".format(
            subjet_prefix,
            self.event_id,
            self.event_service,
            self.event_action,
            self.server
        )

        send_mail(subject, "{0}".format(
            self.get_event_summary()),
            'kairos@mgara.com',
            [to],
            fail_silently=False
            )

        return "Mail Sent to {}".format(to)

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass
