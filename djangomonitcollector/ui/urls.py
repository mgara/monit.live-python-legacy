
from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.dashboard,
        name='dashboard'
    ),
    
    url(
        regex=r'^notifications/$',
        view =views.notifications,
        name='notifications'
    ),

    url(
        regex=r'^dashboard/$',
        view =views.dashboard,
        name='dashboard'
    ),
    url(
        regex=r'^server/update/(?P<pk>\d+)/$',
        view=views.ServerUpdateView.as_view(),
        name='server_update'
    ),
    url(
        regex=r'^server/show/(?P<pk>\d+)/$',
        view=views.ServerShowView.as_view(),
        name='server_show'
    ),
    url(
        regex=r'^server/((?P<pk>\d+))/alerts/list/$',
        view=views.EventListView.as_view(),
        name='server_alerts'
    ),
    url(
        regex=r'^server/(?P<server_id>\d+)/$',
        view=views.server,
        name='server'    
    ),
    url(
        regex=r'^server/(?P<server_id>\w+)/process/(?P<process_name>[^/]+)/$',
        view=views.process,
        name='process'    
    ),
    # actions
    url(
        regex=r'^process_action/(?P<server_id>\d+)/$',
        view=views.process_action,
        name='process_action'    
    ),
    url(
        regex=r'^confirm_delete/(?P<server_id>\d+)/$',
        view=views.confirm_delete,
        name='confirm_delete'    
    ),
    url(
        regex=r'^delete_server/(?P<server_id>\d+)/$',
        view=views.delete_server,
        name='delete_server'    
    ),

    # json interfaces
    url(
        regex=r'^load_system_data/(?P<server_id>\d+)/$',
        view=views.load_system_data,
        name='load_system_data'    
    ),
    url(
        regex=r'^load_process_data/(?P<server_id>\d+)/(?P<process_name>[^/]+)/$',
        view=views.load_process_data,
        name='load_process_data'    
    ),
    url(
        regex=r'^load_dashboard_table/$',
        view=views.load_dashboard_table,
        name='load_dashboard_table'    
    ),
    url(
        regex=r'^load_system_table/(?P<server_id>\d+)/$',
        view=views.load_system_table,
        name='load_system_table'    
    ),
    url(
        regex=r'^load_process_table/(?P<server_id>\d+)/(?P<process_name>[^/]+)/$',
        view=views.load_process_table,
        name='load_process_table'    
    ),
    url(
        regex=r'ackevent/$',
        view = views.ack_event,
        name='ack_event'
    ),
]
