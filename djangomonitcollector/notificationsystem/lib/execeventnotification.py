__author__ = 'mehergara'
from ieventnotification import IEventSettingsInterface
from parameter import Parameter
import subprocess
import os

class ExecEventNotification(IEventSettingsInterface):

    extra_params = {
        'exec_command': Parameter('exec_command','Exec Command'),
    }


    def process(self):
     #   FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess
        OUTPUT_PLUGIN = open("/tmp/output_plugin", 'w')
        exec_command = self.extra_params['exec_command']
        subprocess.call(exec_command, stdout=OUTPUT_PLUGIN, stderr=OUTPUT_PLUGIN, shell=True)

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass

