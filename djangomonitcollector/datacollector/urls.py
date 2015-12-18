
from django.conf.urls import url

urlpatterns = [

    url(
        r'^collector/(.*)$',
        'djangomonitcollector.datacollector.views.collector',
        name='collector'
    ),

]
