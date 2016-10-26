import os
import subprocess
from ieventnotification import EventSettingsInterface
from parameter import Parameter


class ExecEventNotification(EventSettingsInterface):
    extra_params = {
        'exec_command': Parameter('exec_command', 'Exec Command', '', 'The executable to call here ... use it at your own risk !'),
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

        err_file = self.get_err_output()
        output_file = self.get_std_output()

        # FNULL = open(os.devnull, 'w')    #use this if you want to suppress
        # output to stdout from the subprocess
        OUTPUT_PLUGIN = open(output_file, 'w')
        ERR_PLUGIN = open(err_file, 'w')

        exec_command = self.extra_params['exec_command']
        subprocess.call(
            exec_command, stdout=OUTPUT_PLUGIN, stderr=ERR_PLUGIN, shell=False)
        return ""

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass
