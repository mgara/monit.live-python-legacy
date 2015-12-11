from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import requests

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from models import collect_data, Server, Process, System

monit_update_period = getattr(settings, 'MONIT_UPDATE_PERIOD', 60)
enable_buttons = getattr(settings, 'ENABLE_BUTTONS', False)
monit_user = getattr(settings, 'MONIT_USER', "")
monit_password = getattr(settings, 'MONIT_PASSWORD', "")
monit_port = str(getattr(settings, 'MONIT_PORT', 2812))


@csrf_exempt
def collector(request):
    # only allow POSTs
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = request.body

    collected = collect_data(data)
    if not collected:
        return HttpResponse('wrong data format')
    return HttpResponse('ok')
