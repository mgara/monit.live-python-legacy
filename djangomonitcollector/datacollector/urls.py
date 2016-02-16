from django.conf.urls import url

urlpatterns = [
    url(
            r'^collector/(.*)$',
            'djangomonitcollector.datacollector.views.collector',
            name='collector'
    ),
    url(
            r'^get_servers/$',
            'djangomonitcollector.datacollector.views.list_servers',
            name='list_servers'
    ),
]
