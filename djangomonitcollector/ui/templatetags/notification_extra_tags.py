import ast

from django import template

from  djangomonitcollector.notificationsystem.forms import \
    EVENT_STATUS_CHOICES, \
    EVENT_ACTION_CHOICES, \
    EVENT_STATE_CHOICES

register = template.Library()


@register.filter
def check_size(data):
    if data and len(data) > 0:
        return True
    return False


@register.filter
def parse_service_list(data):
    service_list = ast.literal_eval(data)
    output = '<ul style="list-style: none; ">'
    for service in service_list:
        output = '{0}<li > <h5> <span class="label label-info" >{1}</span></h5> </li>'.format(
            output, service)
    return "{0}</ul>".format(output)


@register.filter
def parse_notification_type(data):
    return to_string(data, EVENT_STATUS_CHOICES)


@register.filter
def parse_notification_state(data):
    return to_string(data, EVENT_STATE_CHOICES)


@register.filter
def parse_notification_action(data):
    return to_string(data, EVENT_ACTION_CHOICES)


def to_string(data, lookup_tuple):
    notification_type_list = ast.literal_eval(data)
    output = '<ul style="list-style: none; ">'
    for nt_type in notification_type_list:
        output = '{0}<li ><h5> <span class="label label-info" >{1}</span></h5> </li>'.format(output,
                                                                                             from_value(int(nt_type),
                                                                                                        lookup_tuple))
    return "{0}</ul>".format(output)


def from_value(value, list_of_items):
    for _type in list_of_items:
        if _type[0] == value:
            return _type[1]
