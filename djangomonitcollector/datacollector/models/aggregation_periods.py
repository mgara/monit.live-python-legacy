from django.db import models
from ordered_model.models import OrderedModel
from django.core.urlresolvers import reverse


GRANULARITY = (
    (10, '10 Seconds'),
    (60, '1 Minute'),
    (300, '5 Minutes'),
    (600, '10 Minutes'),
    (3600, 'Archiving'),
)

PERIOD = (
    (1, 'Hours'),
    (2, 'Days'),
    (3, 'Months'),
    (4, 'Years'),
)


class AggregationPeriod(OrderedModel):
    granularity = models.IntegerField(choices=GRANULARITY)
    period = models.IntegerField(choices=PERIOD)
    number_of_period = models.IntegerField()

    def get_absolute_url(self):
        return reverse('ui:aggregation')
