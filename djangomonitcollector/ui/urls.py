from . import views
from django.conf.urls import url


urlpatterns = [

    url(
        regex=r'^$',
        view=views.dashboard,
        name='dashboard'
    ),
    url(
        regex=r'^notifications/$',
        view=views.notifications,
        name='notifications'
    ),

    url(
        regex=r'^dashboard/$',
        view=views.dashboard,
        name='dashboard'
    ),
    url(
        regex=r'^server/update/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        view=views.ServerUpdateView.as_view(),
        name='server_update'
    ),
    url(
        regex=r'^server/delete/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        view=views.ServerDeleteView.as_view(),
        name='server_delete'
    ),
    url(
        regex=r'^server/show/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        view=views.ServerShowView.as_view(),
        name='server_show'
    ),
    url(
        regex=r'^server/kpis/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        view=views.serverkpis,
        name='server_kpis'
    ),
    url(
        regex=r'^server/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/alerts/list/$',
        view=views.EventListView.as_view(),
        name='server_alerts'
    ),
    url(
        regex=r'^server/(?P<server_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        view=views.server,
        name='server'
    ),
    url(
        regex=r'^server/(?P<server_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/process/(?P<process_name>[^/]+)/$',
        view=views.process,
        name='process'
    ),
    url(
        regex=r'^server/(?P<server_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/filesystem/(?P<filesystem_id>[^/]+)/$',
        view=views.filesystem,
        name='filesystem'
    ),
    url(
        regex=r'^server/(?P<server_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/network/(?P<network_name>[^/]+)/$',
        view=views.network,
        name='network'
    ),
    url(
        regex=r'^confirm_delete/(?P<server_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        view=views.confirm_delete,
        name='confirm_delete'
    ),
    url(
        regex=r'^delete_server/(?P<server_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        view=views.delete_server,
        name='delete_server'
    ),
    url(
        regex=r'ackevent/$',
        view=views.ack_event,
        name='ack_event'
    ),
    url(
        regex=r'^load_dashboard_table/$',
        view=views.load_dashboard_table,
        name='load_dashboard_table'
    ),
    url(
        regex=r'settings/(?P<pk>.*)/$$',
        view=views.SettingsUpdateView.as_view(),
        name='settings_update'
    ),
    url(
        regex=r'intellievent/$',
        view=views.IntelliEvent.as_view(),
        name='intellievent'
    ),
    url(
        regex=r'intellievent2/$',
        view=views.intellievent_list,
        name='intellievent_2'
    ),
    url(
        regex=r'update_hgs/$',
        view=views.update_user_hgs,
        name='update_hgs'
    ),
    url(
        regex=r'set_stats_period/$',
        view=views.set_stats_period,
        name='set_stats_period'
    ),
    url(
        regex=r'last_week_events/$',
        view=views.get_weeks_events,
        name='last_week_events'
    ),
    url(
        regex=r'today_events/$',
        view=views._get_todays_events,
        name='today_events'
    ),

]
