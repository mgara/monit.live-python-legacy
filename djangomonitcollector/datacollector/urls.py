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

    url(r'^delete/(.+)/$',
        delete_server,
        name='delete_server'),
    url(
        r'^collector/(.+)/$',
        collector,
        name='collector'
    ),
    url(
        r'^collector/(.+)/(?P<host_group>.+)/$',
        collector,
        name='collector_with_host_group'
    ),
    url(
        r'^get_servers/$',
        list_servers,
        name='list_servers'
    ),
]
