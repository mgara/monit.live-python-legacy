from django.core.mail import send_mail

from ieventnotification import IEventSettingsInterface
from parameter import Parameter


class EmailEventNotification(IEventSettingsInterface):
    extra_params = {
        'to': Parameter('to', 'To'),
        'subjet_prefix': Parameter('subjet_prefix', 'Subject Prefix'),
    }

    def __init__(self):
        pass

    def process(self):
        subjet_prefix = self.extra_params['subjet_prefix']
        to = self.extra_params['to']
        subject = "{0}:[{1}] on [{4}/{2}] action [{3}]".format(
                subjet_prefix,
                self.event_status,
                self.event_service,
                self.event.event_action,
                self.server
        )

        send_mail(subject, "{0}".format(self.get_event_summary()), 'meher.gara@gmail.com',
                  [to], fail_silently=False)

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass
