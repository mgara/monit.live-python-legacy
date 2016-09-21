# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'del_api_key/$',
        view=views.delete_api_key,
        name='delete_api_key'
    ),
    url(
        regex=r'new_api_key/$',
        view=views.new_api_key,
        name='new_api_key'
    ),
    url(
        regex=r'update_user_settings/$',
        view=views.update_user_settings,
        name='update_user_settings'
    ),
    url(
        r'^create/$',
        views.UserCreate.as_view(),
        name='create'
    ),
    url(
        regex=r'newck/$',
        view=views.new_collector_key,
        name='new_collector_key'
    ),
    url(
        regex=r'delck/$',
        view=views.delete_collector_key,
        name='delete_collector_key'
    ),

    # URL pattern for the UserListView
    url(
        regex=r'^$',
        view=views.UserListView.as_view(),
        name='index'
    ),

    # URL pattern for the UserRedirectView
    url(
        regex=r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),

    # URL pattern for the UserDetailView
    url(
        regex=r'^(?P<username>[\w.@+-]+)/$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the UserUpdateView
    url(
        regex=r'^update/(?P<pk>.+)/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),

    url(r'^delete/(?P<username>[\w.@+-]+)/$',
        views.UserDeleteView.as_view(), name='delete'),
    url(r'^update_password/(?P<pk>.+)/$',
        views.UpdatePasswordForUser, name='update_password'),
    url(r'^update_password/$', views.UpdatePassword,
        name='update_password_cu'),



]
