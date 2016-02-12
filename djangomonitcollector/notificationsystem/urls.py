
from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        regex=r'^notificationtype/get_plugin_form/$',
        view=views.get_notification_plugin_form,
        name='get_plugin_form'
    ),
    url(
        regex=r'^notificationtype/create/$',
        view=views.NotificationTypeCreate.as_view(),
        name='notificationtype_create'
    ),
    url(
        regex=r'^notificationtype/show/(?P<pk>[0-9a-z]+)/$',
        view=views.NotificationTypeView.as_view(),
        name='notificationtype_view'
    ),
    url(
        regex=r'^notificationtype/mute/(?P<pk>[0-9a-z]+)/$',
        view=views.notificationtype_mute_all,
        name='notification_mute_all'
    ),
    url(
        regex=r'^notificationtype/update/(?P<pk>[0-9a-z]+)/$',
        view=views.NotificationTypeUpdate.as_view(),
        name='notificationtype_update'
    ),
    url(
        regex=r'^notificationtype/toggle/(?P<pk>[0-9a-z]+)/$',
        view=views.notificationtypeactivation,
        name='notificationtype_activation'
    ),
    url(
        regex=r'^notificationtype/delete/(?P<pk>[0-9a-z]+)/$',
        view=views.NotificationTypeDelete.as_view(),
        name='notificationtype_delete'
    ),
    url(
        regex=r'^notificationtype/list/$',
        view=views.NotificationTypeListView.as_view(),
        name='notificationtype_list'
    )
    

]