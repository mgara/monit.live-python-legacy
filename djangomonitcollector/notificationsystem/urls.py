
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
        regex=r'^notificationtype/((?P<pk>\d+))/alerts/list/$',
        view=views.NotificationTypeListView.as_view(),
        name='notificationtype_list'
    )
]