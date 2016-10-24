import os
import subprocess
from ieventnotification import EventSettingsInterface
from parameter import Parameter


class ExecEventNotification(EventSettingsInterface):
    extra_params = {
        'exec_command': Parameter('exec_command', 'Exec Command', '', 'The executable to call here ... use it at your own risk !'),
        'stdr_out': Parameter('stdr_out', 'Standard Output File', '', 'Can be /dev/null, default is /tmp/output_plugin_'),
        'stdr_err': Parameter('stdr_err', 'Standard Error File', '', 'Can be /dev/null, default is /tmp/output_plugin_err_'),
    }

    PLUGIN_NAME = "Exec Notification"
    PLUGIN_ICON = "gears"
    HELP_MESSAGE = "Can be used to execute an arbitrary program and send an alert. If you choose this action you must state the program to be executed and if the program requires arguments you must enclose the program and its arguments in a quoted string. You may optionally specify the uid and gid the executed program should switch to upon start. "
    TOOLTIP = "Exec Notification"

    def process(self):
        os.environ['MONIT_DESCRIPTION'] = str(self.event_message)
        os.environ['MONIT_SERVICE'] = str(self.event_service)
        os.environ['ACTION'] = str(self.event_action)
        os.environ['TYPE'] = str(self.event_type)
        os.environ['STATUS'] = str(self.event_id)
        os.environ['MONIT_HOST'] = str(self.server)

        if self.extra_params['stdr_out']:
            output_file = self.extra_params['stdr_out']
        else:
            output_file = "/tmp/output_plugin_"

        if self.extra_params['stdr_err']:
            err_file = self.extra_params['stdr_err']
        else:
            err_file = "/tmp/output_plugin_err_"

        # FNULL = open(os.devnull, 'w')    #use this if you want to suppress
        # output to stdout from the subprocess
        OUTPUT_PLUGIN = open(output_file, 'w')
        ERR_PLUGIN = open(err_file, 'w')

        exec_command = self.extra_params['exec_command']
        subprocess.call(
            exec_command, stdout=OUTPUT_PLUGIN, stderr=ERR_PLUGIN, shell=False)

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass
