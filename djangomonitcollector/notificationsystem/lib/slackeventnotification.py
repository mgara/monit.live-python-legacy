
from ieventnotification import EventSettingsInterface
from parameter import Parameter
from slacker import Slacker
from django.contrib.sites.models import Site


class SlackEventNotification(EventSettingsInterface):
    extra_params = {
        'slack_api_token': Parameter('slack_api_token', 'Slack API Token'),
        'slack_channel': Parameter('slack_channel', 'Slack Channel'),
        'slack_username': Parameter('slack_username', 'Slack Username')
    }

    PLUGIN_NAME = "Slack Notification"
    PLUGIN_ICON = "slack"

    HELP_MESSAGE = "Sends a Slack notification providing the Slack API token and the channel name. "
    TOOLTIP = "Slack Notification"

    def __init__(self):
        pass

    def process(self):
        site = Site.objects.get_current().domain
        slack_api_token = self.extra_params['slack_api_token']
        slack_channel = self.extra_params['slack_channel']
        slack_username = self.extra_params['slack_username']

        link_to_events = "http://{}/ui/server/{}/".format(
            site, self.event.server.id)
        title = "[{0} event] on [{2}] service [{1}] ".format(
                self.event_id,
                self.event_service,
                self.server
        )

        attachments = [self.get_attachement(title, link_to_events)]
        if not slack_username:
            slack_username = "Monit Collector"
        slack = Slacker(slack_api_token)

        # Send a message to #general channel
        slack.chat.post_message(
            slack_channel, "", username=slack_username, attachments=attachments)

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass

    def get_attachement(self, title, link):

        state_dic = {
            0: "#41DB00",
            1: '#EF002A',
            2: '#2A17B1',
            3: '#150873',
            4: '#FF4F00',
            10: '#9B001C',
        }
        event_color = state_dic[self.event_state_id]
        attachement = {
            "fallback": title,
            "color": event_color,
            "pretext": title,
            "author_name": "{} {}".format(self.event_type, self.event_state),
            "author_link": link,
            "title": self.event_message,
            "fields": [
                {
                    "title": "Host",
                    "value": self.server,
                    "short": False
                },
                {
                    "title": "Service",
                    "value": self.service_name,
                    "short": False
                },
                {
                    "title": "Event State",
                    "value": self.event_state,
                    "short": False
                },
                {
                    "title": "Action Taken",
                    "value": self.event_action,
                    "short": False
                }
            ]


        }

        return attachement
