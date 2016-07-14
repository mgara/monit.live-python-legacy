from django.conf.urls import url

from djangomonitcollector.datacollector.views import OrganisationListView,\
    OrganisationCreateView,\
    OrganisationUpdateView,\
    collector,\
    list_servers,\
    delete_server

urlpatterns = [

    url(r'^organisations/$',
        OrganisationListView.as_view(),
        name='organisations'),

    url(r'^new_organisation/$',
        OrganisationCreateView.as_view(),
        name='new_organisation'),

    url(r'^update_organisation/(?P<pk>.+)/$',
        OrganisationUpdateView.as_view(),
        name='update_organisation'),

    url(r'^delete/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        delete_server,
        name='delete_server'),
    url(
        r'^collector/(?P<collector_key>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        collector,
        name='collector'
    ),
    url(
        r'^collector/(?P<collector_key>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<host_group>.+)/$',
        collector,
        name='collector_with_host_group'
    ),
    url(
        r'^get_servers/$',
        list_servers,
        name='list_servers'
    ),
]
