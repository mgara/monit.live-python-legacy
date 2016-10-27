import os
import subprocess
import shlex
from datetime import datetime
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

        os.environ['MONIT_HOST'] = str(self.server)
        os.environ['MONIT_DATE'] = datetime.today().strftime("%c")
        os.environ['MONIT_EVENT'] = str(self.event_action)

        os.environ['ACTION'] = str(self.event_action)
        os.environ['TYPE'] = str(self.event_type)
        os.environ['STATUS'] = str(self.event_id)

        exec_command = self.extra_params['exec_command']
        args = shlex.split(exec_command)
        process_output = self.run_command(args)

        if process_output['status']:
            output = '\n'.join('{}: {}'.format(*k) for k in enumerate(process_output['output']))
            return output
        else:
            process_output['error'] = process_output['output'] + process_output['error']
            error = '\n'.join('{}: {}'.format(*k) for k in enumerate(process_output['error']))
            raise(StandardError(error))

    def finalize(self, event_object):
        # put whatever you want to be done after the process command
        pass

    def run_command(self, cmd):
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True
            )
        out = "No Output"
        err = "No Error"
        (out, err) = p.communicate()
        ret = p.wait()
        out = filter(None, out.split('\n'))
        err = filter(None, err.split('\n'))
        ret = True if ret == 0 else False
        return dict({'output': out, 'error': err, 'status': ret})
