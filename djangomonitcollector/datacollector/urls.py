
from django.conf.urls import url
from . import views

urlpatterns = [

    url(
        r'^collector$',
        'datacollector.views.collector',
        name='collector'
    ),

]
