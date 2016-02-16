__author__ = 'mehergara'
import os
import subprocess

from ieventnotification import IEventSettingsInterface
from parameter import Parameter


class ExecEventNotification(IEventSettingsInterface):
    extra_params = {
        'exec_command': Parameter('exec_command', 'Exec Command'),
    }

    def process(self):
        os.environ['MESSAGE'] = str(self.event_message)
        os.environ['SERVICE'] = str(self.event_service)
        os.environ['ACTION'] = str(self.event_action)
        os.environ['TYPE'] = str(self.event_type)
        os.environ['STATUS'] = str(self.event_status)
        os.environ['SERVER'] = str(self.server)

        #   FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess
        OUTPUT_PLUGIN = open("/tmp/output_plugin_", 'w')
        exec_command = self.extra_params['exec_command']
        subprocess.call(exec_command, stdout=OUTPUT_PLUGIN, stderr=OUTPUT_PLUGIN, shell=True)

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass
