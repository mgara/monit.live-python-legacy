try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

# place app url patterns here

from djangomonitcollector.users.models import User
from rest_framework import routers
from api.views import UserViewSet
from api import views



# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^online-servers/$', views.OnlineServerList.as_view()),
    url(r'^offline-servers/$', views.OfflineServerList.as_view()),
    url(r'^all-servers/$', views.ServerList.as_view()),
    url(r'^server/(?P<id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$', views.ServerDetail.as_view()),
]
