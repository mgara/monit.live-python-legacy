import ast
import time

from django import template
from django.conf import settings
from django.utils import timezone
import datetime
import pytz
from math import floor

register = template.Library()

try:
    monit_update_period = settings.MONIT_UPDATE_PERIOD
except:
    monit_update_period = 60


@register.filter
def clean(value):
    return str(value).replace('-', '_')


@register.filter
def clean_service_name(value):
    return value.replace("_/", "_").replace("___", "__").replace("__", "_").replace("_", "/")


@register.filter
def format_timedelta(value, time_format="{days} days, {hours2}:{minutes2}:{seconds2}"):
    if not value:
        return "-"

    if hasattr(value, 'seconds'):
        seconds = value.seconds + value.days * 24 * 3600
    else:
        seconds = int(value)

    seconds_total = seconds

    minutes = int(floor(seconds / 60))
    minutes_total = minutes
    seconds -= minutes * 60

    hours = int(floor(minutes / 60))
    hours_total = hours
    minutes -= hours * 60

    days = int(floor(hours / 24))
    days_total = days
    hours -= days * 24

    years = int(floor(days / 365))
    years_total = years
    days -= years * 365

    if days > 0:
        time_format = "{days} days, {hours2}:{minutes2} ago"
    else:
        if hours > 0:
            time_format = "{hours2}h {minutes2}m ago"
        else:
            if minutes > 0:
                time_format = "{minutes2}m ago"
            else:
                if seconds > 20:
                    time_format = "{seconds2}s ago"
                else:
                    time_format = "New !"


    return time_format.format(**{
        'seconds': seconds,
        'seconds2': str(seconds).zfill(2),
        'minutes': minutes,
        'minutes2': str(minutes).zfill(2),
        'hours': hours,
        'hours2': str(hours).zfill(2),
        'days': days,
        'years': years,
        'seconds_total': seconds_total,
        'minutes_total': minutes_total,
        'hours_total': hours_total,
        'days_total': days_total,
        'years_total': years_total,
    })


@register.filter
def time_diff(date):
    if not date:
        return None
    utc_dt = datetime.datetime.utcnow()
    utc_dt = utc_dt.replace(tzinfo=pytz.timezone("UTC"))
    delta = utc_dt - date
    return delta


@register.filter
def get_title(url_name):
    if url_name == "server":
        return "Server"
    if url_name == "dashboard":
        return "Home"
    url_name = url_name.replace('_', ' ')
    return url_name.title()


@register.filter
def server_status_to_css_class(status):
    if status:
        return "<a href=\"#\" class=\"btn btn-primary btn-xs\"><span class=\"glyphicon glyphicon-upload\"></span></a>"
    else:
        return "<a href=\"#\" class=\"btn btn-danger btn-xs\"><span class=\"glyphicon glyphicon-download\"></span></a>"


@register.filter
def boolean_widget(boolean_value):
    if boolean_value:
        return "<a href=\"#\" class=\"btn btn-primary btn-xs\"><span class=\"fa fa-check-square\"></span></a>"
    else:
        return "<a href=\"#\" class=\"btn btn-danger btn-xs\"><span class=\"fa fa-times\"></span></a>"

@register.filter
def event_state_to_widget_style(state):
    if int(state) == 0:
        return "navy"
    if int(state) == 1:
        return "red"
    return "lazur"

@register.filter
def remove_protocol(value):
    return value.replace('https://','').replace('http://','')

@register.filter
def get_server_len(server_set):
    if not server_set:
        return 0
    return len(server_set.all())


@register.filter
def status_to_label(status):
    if status:
        return "Disable"
    else:
        return "Enable"


@register.filter
def extra_params(xtra):
    xtra_params = ast.literal_eval(xtra)
    output = "<ul>"
    for x in xtra_params:
        output += "<li><b>{0}</b>: [{1}]</li>".format(x, xtra_params[x])
    output = "{0}</ul>".format(output)
    return output


@register.filter
def timestamp_to_date(timestamp):
    if not isinstance(timestamp, int):
        return ""
    data_tz = pytz.timezone("UTC")
    user_tz = timezone.get_current_timezone()
    data_time = datetime.datetime.fromtimestamp(timestamp, tz=data_tz)

    user_time = user_tz.normalize(data_time.astimezone(user_tz))
    return user_time

@register.filter
def to_html(txt):
    return txt.replace("\n", "<br/>")


@register.filter
def time_class(timestamp):
    if not isinstance(timestamp, int):
        return ""
    if int(time.time()) > int(timestamp) + 3 * monit_update_period:
        return "danger"
    return "primary"


@register.filter
def to_path(dir_name):
    return dir_name.replace("_", "/")


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
    if not alert_counts:
        return ""
    if int(alert_counts) == 0:
        return ""
    return "danger"


@register.filter
def status_tr_class(status, monitor):
    if not monitor:
        return 'sucess'
    if monitor == 0:
        return 'info'
    if int(status) == 0:
        return 'primary'
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
    return None

# the grey button to highlight a row in the alert table.
@register.filter
def to_btn(value):
    var = '{}'
    if value:
        return "<button onclick=\"$('#event-{0}').effect('highlight', {1}, 1500);\" class=\"btn btn-reverse btn-xs\" type=\"button\" id=\"highlight-{0}\" data-id=\"{0}\">{0}</button>".format(value,var)

@register.filter
def to_btns(value):
    out = ""
    if value:
        table = ast.literal_eval(value)

        for event_id in table:
            out += to_btn(event_id)
    return out


@register.filter
def to_icon(value):
    if value:
        return "<i class=\"fa fa-exclamation-triangle\"></i>"
    return ""


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
    progress_bar_txt = "{0}% [{1}/{2}]".format(percent_value, disk_size_formatting(
        fs.blocks_usage_last), disk_size_formatting(fs.blocks_total))
    return get_progress_bar_html(percent_value, progress_bar_txt)


@register.filter
def fs_percent_bar_inode(fs):
    value = fs.inode_percent_last if fs.inode_percent_last else 0.0
    percent_value = round(value, 1)
    progress_bar_txt = "{0}% [{1}/{2}]".format(
        percent_value, get_int(fs.inode_usage_last), get_int(fs.inode_total))
    return get_progress_bar_html(percent_value, progress_bar_txt)


@register.filter
def percent_to_bar(percent):
    value = percent if percent else 0.0
    percent_value = round(value, 1)
    progress_bar_txt = "{0}%".format(value)
    return get_progress_bar_html(percent_value, progress_bar_txt)


@register.filter
def status_to_string(status, p):
    if not p:
        return "not p"
    if not status:
        return "not status"
    type_of_service = p.service_type
    monitor_status = p.monitor
    return status_to_string_(status, type_of_service, monitor_status)


@register.filter  # Event type
def type_to_string(type):
    array_type = ["FileSystem", "Directory", "File", "Process",
                  "Remote Host", "System", "Fifo", "Program", "Network"]
    return array_type[int(type)]


@register.filter  # Event id
def event_status_to_string(status):
    status_int = int(status)
    state_dic = {
        1: 'checksum',
        2: 'resource',
        4: 'timeout',
        8: 'timestamp',
        16: 'size',
        32: 'connection',
        64: 'permission',
        128: 'UID',
        256: 'GID',
        512: 'nonexist',
        1024: 'invalid',
        2048: 'data',
        4096: 'exec',
        8192: 'fsflags',
        16384: 'icmp',
        32768: 'content',
        65536: 'instance',
        131072: 'action',
        262144: 'PID',
        524288: 'PPID',
        1048576: 'heartbeat',
        16777216: 'link mode/speed',
        2097152: 'status',
        4194304: 'uptime',
        8388608: 'linkstatus'
    }

    try:
        return state_dic[status_int]
    except:
        return status_int


@register.filter  # Event State
def event_state_to_string(state):
    state_int = int(state)
    state_dic = {
        0: 'Success',
        1: 'Error',
        2: 'Change',
        3: 'Link mode not changed',
        4: 'Host Down',
        10: 'Info',
        11: 'Critical',
    }
    return state_dic[state_int]


@register.filter  # Event Action
def action_to_string(action):
    action_int = int(action)
    action_dict = {
        1: 'Alert',
        2: 'Restart',
        3: 'Stop',
        4: 'Exec',
        5: 'Unmonitor',
        6: 'Reload',
    }
    return action_dict[action_int]


@register.filter
def event_state_to_style(state):
    if int(state) == 0:
        return "primary"
    if int(state) == 1:
        return "danger"
    return "success"


@register.filter
def flapping_status(flapping):
    if flapping:
        return '<span class="label label-danger small">Yes</span>'
    else:
        return '<span class="label label-primary small">No</span>'


def status_to_string_(status, type_of_service, monitor_status):
    ok_status = ['Accessible', 'OK', 'File exists', 'Running',
                 'Online with all services', 'System OK', 'OK', 'Program Is Running', 'UP']
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


def get_progress_bar_html(value, display_txt):
    style = get_style_from_value(value)
    res = '<span class="label label-{0} small">{2}</span>' \
          '<div class="progress progress-mini">' \
          '<div class="progress-bar progress-bar-{0} " role="progressbar" aria-valuenow="40" aria-valuemin="0" aria-valuemax="100" style="width: {1}%">' \
          '<span>{2}</span>' \
          '</div>' \
          '</div>'.format(style, value, display_txt)
    return res


def get_style_from_value(value, thresh1=50, thresh2=85):
    if value < thresh1:
        return "primary"
    if value >= thresh1 and value < thresh2:
        return "warning"
    return "danger"


@register.simple_tag
def get_current_notification_number():
    return 999
    pass


@register.filter
def nt_status_to_label(status):
    if status:
        return '<span class="label label-primary small">On</span>'
    return '<span class="label label-danger small">Off</span>'


@register.filter
def get_skin_name(value):
    skin_dic = dict()
    skin_dic["default"] = "Default Skin"
    skin_dic["-"] = "Default Skin"
    skin_dic["skin-1"] = "Azure"
    skin_dic["skin-2"] = "Navy Blue"
    skin_dic["skin-3"] = "Sahara"

    return skin_dic[value]
