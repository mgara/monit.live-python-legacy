from django.http import HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from models.server import collect_data


@csrf_exempt
def collector(request, collector_key):
    # only allow POSTs
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = request.body

    collected, status = collect_data(data, collector_key)
    if not collected:
        print status
        response = JsonResponse({'error': status, 'status': '500'}, status=500)
        return response
    return JsonResponse({'message': '200 OK'})
