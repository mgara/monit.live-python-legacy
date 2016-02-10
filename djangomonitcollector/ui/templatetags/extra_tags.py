import time

from django import template
from django.utils import timezone
from django.conf import settings

register = template.Library()

try:
    monit_update_period = settings.MONIT_UPDATE_PERIOD
except:
    monit_update_period = 60


@register.filter
def timestamp_to_date(timestamp):
    if not isinstance(timestamp, int):
        return ""
    return timezone.datetime.fromtimestamp(timestamp)

@register.filter
def to_html(txt):
    return txt.replace("\n","<br/>")

@register.filter
def time_class(timestamp):
    if not isinstance(timestamp, int):
        return ""
    if int(time.time()) > int(timestamp) + 3 * monit_update_period:
        return "danger"
    return "success"


@register.filter
def time_str(uptime):
    """ converts uptime in seconds to a time string """
    if not isinstance(uptime, int):
        return "-"
    mins = (uptime / 60) % 60
    hours = (uptime / 60 / 60) % 24
    days = (uptime / 24 / 60 / 60) % 365
    years = uptime / 365 / 24 / 60 / 60
    if years == 0:
        if days == 0:
            if hours == 0:
                return "%sm" % mins
            return "%sh %sm" % (hours, mins)
        return "%sd %sh %sm" % (days, hours, mins)
    return "%sy %sd %sh %sm" % (years, days, hours, mins)

@register.filter
def status_alert(alert_counts):
    if not alert_counts :
        return "success"
    if int(alert_counts) == 0:
        return "sucess"
    return "danger"

@register.filter
def status_tr_class(status, monitor):
    if monitor == 0:
        return 'info'
    if int(status) == 0:
        return 'success'
    return 'danger'


@register.filter
def human_readable_size(value):
    if value:
        return sizeof_fmt(value)
    return "-"

@register.filter
def kb_formatting(value):
    if value:
        return sizeof_fmt(value * 1024.0)
    return "-"

@register.filter
def disk_size_formatting(value):
    if value:
        return sizeof_fmt(value * 1024.0 * 1024.0)
    return "-"

@register.filter
def format_number(value):
    if value:
        return "{:,}".format(value)

    return "-"


@register.filter
def get_int(value):
    if value:
        return int(value)
    return "-"

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


@register.filter
def percent(value):
    try:
        if not isinstance(value, (float, basestring)):
            return ""
        return str(round(value, 1)) + "%"
    except:
        return "Error parsing {0}".format(value)

@register.filter
def fs_percent_bar(fs):
    value = fs.blocks_percent_last if fs.blocks_percent_last else 0.0
    percent_value = round(value, 1)
    progress_bar_txt=  "{0}% [{1}/{2}]".format(percent_value,disk_size_formatting(fs.blocks_usage_last),disk_size_formatting(fs.blocks_total))
    return get_progress_bar_html(percent_value,progress_bar_txt)

@register.filter
def fs_percent_bar_inode(fs):
    value = fs.inode_percent_last if fs.inode_percent_last else 0.0
    percent_value = round(value, 1)
    progress_bar_txt=  "{0}% [{1}/{2}]".format(percent_value,get_int(fs.inode_usage_last),get_int(fs.inode_total))
    return get_progress_bar_html(percent_value,progress_bar_txt)

@register.filter
def percent_to_bar(percent):
    value = percent if percent else 0.0
    percent_value = round(value, 1)
    progress_bar_txt=  "{0}%".format(value)
    return get_progress_bar_html(percent_value,progress_bar_txt)

@register.filter
def type_to_string(type):
    array_type =["FileSystem","Directory","File","Process","Remote Host","System","Fifo","Program","Network"]
    return array_type[int(type)]


@register.filter
def status_to_string(status,p):
    type_of_service=p.service_type
    monitor_status=p.monitor
    return status_to_string_(status,type_of_service,monitor_status)

@register.filter
def event_status_to_string(status):
    status_int = int(status)
    state_dic = {
    1:'checksum',
    2:'resource',
    4:'timeout',
    8:'timestamp',
    16:'size',
    32:'connection',
    64:'permission',
    128:'UID',
    256:'GID',
    512:'nonexist',
    1024:'invalid',
    2048:'data',
    4096:'exec',
    8192:'fsflags',
    16384:'icmp',
    32768:'content',
    65536:'instance',
    131072:'action',
    262144:'PID',
    524288:'PPID',
    1048576:'heartbeat',
    16777216:'link mode/speed',
    2097152:'status',
    4194304:'uptime'
    }


    try:
        return state_dic[status_int]
    except: 
        return status_int

@register.filter
def event_state_to_string(state):
    state_int = int(state)
    state_dic = {
        0:'Success',
        1:'Error',
        2:'Change',
        3:'Link mode not changed'
    }
    return state_dic[state_int]


@register.filter
def action_to_string(action):
    action_int = int(action)
    action_dict = {
        1:'1:ALERT (monit alert generated)',
        2:'2:RESTART (trying to restart)',
        3:'3:STOP',
        4:'4:EXEC',
        5:'5:UNMONITOR',
        6:'6:RELOAD',
    }
    return action_dict[action_int]

@register.filter
def event_state_to_style(state):
    if int(state) ==0:
        return "success"
    if int(state) ==1:
        return "danger"
    return "info"

def status_to_string_(status,type_of_service,monitor_status):
    ok_status = ['Accessible', 'OK', 'File exists', 'Running', 'Online with all services', 'System OK', 'OK', 'Program Is Running', 'UP']
    errors_messages = ['Ok', 'Checksum failed', 'Resource limit matched', 'Timeout', 'Timestamp failed', 'Size failed',
                       'Connection failed', 'Permission failed', 'UID failed', 'GID failed', 'Does not exist',
                       'Invalid type', 'Data access error', 'Execution failed', 'Changed', 'ICMP failed']
    monitor = ['Not monitored', 'Yes', 'Initializing']

    if monitor_status != 1:
        return monitor[monitor_status]

    # format to a bitarray
    bits = '{0:015b}'.format(int(status))
    out_str = ''
    ok = True
    for i in range(len(bits)):
        if bits[i] == "1":
            if not ok:
                out_str += ", "
            out_str += errors_messages[-i - 1]
            ok = False
    if ok:
        return ok_status[type_of_service]

    return out_str


def get_progress_bar_html(value,display_txt):
    style = get_style_from_value(value)
    res = '<span class="label label-{0} small">{2}</span>'\
          '<div class="progress">' \
          '<div class="progress-bar progress-bar-{0}" role="progressbar" aria-valuenow="40" aria-valuemin="0" aria-valuemax="100" style="width: {1}%">' \
          '<span>{2}</span>'\
          '</div>' \
          '</div>'.format(style,value,display_txt)
    return res

def get_style_from_value(value,thresh1=50,thresh2=85):
    if value < thresh1:
        return "success"
    if value >=thresh1 and value < thresh2:
        return "warning"
    return "danger"