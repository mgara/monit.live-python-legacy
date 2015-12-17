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
    return "N/A"

@register.filter
def kb_formatting(value):
    if value:
        return sizeof_fmt(value * 1024.0)
    return "N/A"

@register.filter
def format_number(value):
    if value:
        return "{:,}".format(value)

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
        return "NaN {0}".format(value)


@register.filter
def status_to_string(status,p):
    type_of_service=p.service_type
    monitor_status=p.monitor
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
