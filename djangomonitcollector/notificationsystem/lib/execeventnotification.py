__author__ = 'mehergara'
from ieventnotification import IEventSettingsInterface

class ExecEventNotification(IEventSettingsInterface):

    def __init__(self):
        pass

    def set_exec(self, exec_command):
        self.EXEC = "/usr/bin/echo 'test' > /root/notifications"

    def process(self):
        pass
