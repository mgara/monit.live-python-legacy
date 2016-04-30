from django import template
register = template.Library()


GRANULARITY = {
    10: '10 Seconds',
    60: '1 Minute',
    300: '5 Minutes',
    600: '10 Minutes',
    3600: '1 Hour',
}

PERIOD = {
    1: 'Hour(s)',
    2: 'Day(s)',
    3: 'Month(s)',
    4: 'Year(s)',
}


@register.filter
def aggregation_period(value):
    return PERIOD[int(value)]


@register.filter
def granularity(value):
    return GRANULARITY[int(value)]
