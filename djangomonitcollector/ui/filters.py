from __future__ import unicode_literals, absolute_import

import django_filters
from django_filters import ChoiceFilter, DateFromToRangeFilter
from ..datacollector.models.server import MonitEvent
from ..datacollector.lib.event_mappings import EVENT_STATE_CHOICES, EVENT_ID_CHOICES, EVENT_TYPE_CHOICES


class IntelliEventsFilter(django_filters.FilterSet):
    event_message = django_filters.CharFilter(lookup_expr='icontains')
    event_id = ChoiceFilter(choices=EVENT_ID_CHOICES)
    event_type = ChoiceFilter(choices=EVENT_TYPE_CHOICES)
    event_state = ChoiceFilter(choices=EVENT_STATE_CHOICES)
    event_time = DateFromToRangeFilter()
    EMPTY_CHOICE = ('', '-------- Show all --------')

    def __init__(self, *args, **kwargs):
        super(IntelliEventsFilter, self).__init__(*args, **kwargs)
        # add empty choice to all choice fields:
        choices = filter(
            lambda f: isinstance(self.filters[f], ChoiceFilter),
            self.filters)
        for field_name in choices:
            extended_choices = ((self.EMPTY_CHOICE,) +
                                self.filters[field_name].extra['choices'])
            self.filters[field_name].extra['choices'] = extended_choices
        # First field - from 09/14/2016 12:00 AM
        self.form.fields['event_time'].fields[
            0].input_formats = ['%m/%d/%Y %H:%M %p']
        # Last field - to
        self.form.fields[
            'event_time'].fields[-1].input_formats = ['%m/%d/%Y %H:%M %p']

    class Meta:
        model = MonitEvent
        fields = [
            'server',
            'service',
            'event_type',
            'event_id',
            'event_state',
            'event_message',
            'event_time',
            'alarm_raised',
            'is_ack',
        ]
        order_by = ['-id']

    def filter_server(self, queryset, value):
        return queryset.filter(
            server__organisation=value
        )
