
from httplib import HTTPConnection
from urlparse import urlparse

from ieventnotification import EventSettingsInterface
from parameter import Parameter


class PostEventNotification(EventSettingsInterface):
    extra_params = {
        'url': Parameter('url', 'URL'),
        'http_header': Parameter('http_header', 'HTTP_HEADER_1'),

    }

    PLUGIN_NAME = "Post2Url"
    PLUGIN_ICON = "send"

    def process(self):
        url = self.extra_params['url']
        return self.post(url, self.get_event_summary())

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass

    def post(settings, url, data):
        urlparts = urlparse(url)
        conn = HTTPConnection(urlparts.netloc, urlparts.port)
        conn.request("POST", urlparts.path, data)
        resp = conn.getresponse()
        body = resp.read()
        return body
