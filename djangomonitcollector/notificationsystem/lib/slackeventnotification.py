
from ieventnotification import EventSettingsInterface
from parameter import Parameter
from slacker import Slacker


class SlackEventNotification(EventSettingsInterface):
    extra_params = {
        'slack_api_token': Parameter('slack_api_token', 'Slack API Token'),
        'slack_channel': Parameter('slack_channel', 'Slack Channel'),
        'monit_collector_server': Parameter('monit_collector_server', 'Collector Server'),

    }

    def __init__(self):
        pass

    def process(self):
        slack_api_token = self.extra_params['slack_api_token']
        slack_channel = self.extra_params['slack_channel']
        monit_collector_server = self.extra_params['monit_collector_server']

        link_to_events = "http://{}/ui/server/{}/".format(monit_collector_server,self.event.server.id)
        title = "[{0} event] on [{2}] service [{1}] ".format(
                self.event_id,
                self.event_service,
                self.server
        )

        attachments = [self.get_attachement(title, link_to_events)]

        slack = Slacker(slack_api_token)

        # Send a message to #general channel
        slack.chat.post_message(slack_channel, "",username="Monit Collector" , attachments=attachments)

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
                    "value": self.event_service,
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
