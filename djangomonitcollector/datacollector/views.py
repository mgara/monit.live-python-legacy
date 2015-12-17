from django.http import HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
import time

from models.server import collect_data

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

    collected, status = collect_data(data)
    if not collected:
        f = open('workfile_{0}.xml'.format(time.time()), 'w')
        f.write(data)
        print status
        response = JsonResponse({'error': status, 'status': '500'}, status=500)
        return response
    return JsonResponse({'message': '200 OK'})
