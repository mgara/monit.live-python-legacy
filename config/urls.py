# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from django.views.generic.base import RedirectView
from rest_framework_swagger.views import get_swagger_view
from django.conf import settings # import the settings file



favicon_view = RedirectView.as_view(url='/static/favicon/favicon.ico', permanent=True)
favicon_16_view = RedirectView.as_view(url='/static/favicon/favicon-16x16.png', permanent=True)
favicon_32_view = RedirectView.as_view(url='/static/favicon/favicon-32x32.png', permanent=True)
apple_touch_icon = RedirectView.as_view(url='/static/favicon/apple-touch-icon.png', permanent=True)
android_manifest = RedirectView.as_view(url='/static/favicon/manifest.json', permanent=True)
safari_pinned_tab = RedirectView.as_view(url='/static/favicon/safari-pinned-tab.svg', permanent=True)

app_name = settings.APPNAME
api_version = settings.APIVERSION


schema_view = get_swagger_view(title="{} API v{}".format(app_name, api_version))

urlpatterns = [


    #Restful API
    url(r'^v1/$', schema_view),
    url(r'^v1/', include("api.urls")),

    #Favicons
    url(r'^favicon\.ico$', favicon_view),
    url(r'^favicon\-16x16\.png$', favicon_16_view),
    url(r'^favicon\-32x32\.png$', favicon_32_view),
    url(r'^apple\-touch\-icon\.png$', apple_touch_icon),
    url(r'^manifest\.json$', android_manifest),
    url(r'^safari\-pinned\-tab\.svg$', safari_pinned_tab),


    #Home
    url(r'^$', 'djangomonitcollector.ui.views.dashboard', name="home"),

    #About
    url(r'^about/$',
        TemplateView.as_view(template_name='pages/about.html'), name="about"),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/',
        include("djangomonitcollector.users.urls", namespace="users")),
    url(r'^accounts/', include('allauth.urls')),

    # DataCollector
    url(r'^dc/', include("djangomonitcollector.datacollector.urls",
                         namespace="datacollector")),

    #UI
    url(r'^ui/', include("djangomonitcollector.ui.urls", namespace="ui")),

    #Notification
    url(r'^notification/',
        include("djangomonitcollector.notificationsystem.urls", namespace="n")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request),
        url(r'^403/$', default_views.permission_denied),
        url(r'^404/$', default_views.page_not_found),
        url(r'^500/$', default_views.server_error),
    ]
