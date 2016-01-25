
from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        regex=r'^notificationtype/create/$',
        view=views.NotificationTypeCreate.as_view(),
        name='notificationtype_create'
    ),
    url(
        regex=r'^notificationtype/show/(?P<pk>\d+)/$',
        view=views.NotificationTypeView.as_view(),
        name='notificationtype_view'
    ),
    url(
        regex=r'^notificationtype/update/(?P<pk>\d+)/$',
        view=views.NotificationTypeUpdate.as_view(),
        name='notificationtype_update'
    ),
    url(
        regex=r'^notificationtype/list/$',
        view=views.NotificationTypeListView.as_view(),
        name='notificationtype_list'
    ),
    url(
        regex=r'^notification/show/(?P<pk>\d+)/$',
        view=views.NotificationView.as_view(),
        name='notification_view'
    ),
    url(
        regex=r'^notification/delete/(?P<pk>\d+)/$',
        view=views.NotificationDelete.as_view(),
        name='notification_delete'
    ),
    url(
        regex=r'^notification/list/$',
        view=views.NotificationListView.as_view(),
        name='notification_list'
    )
]