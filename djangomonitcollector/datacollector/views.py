from django.http import HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from models.server import collect_data, Server





def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def collector(request, collector_key):
    # only allow POSTs
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = request.body
    ip_addr = get_client_ip(request)
    collected, status = collect_data(data, collector_key,ip_addr)
    logger.debug(data)
    if not collected:
        # log
        print status
        response = JsonResponse({'error': status, 'status': '500'}, status=500)
        return response
    return JsonResponse({'message': '200 OK'})


@csrf_exempt
def list_servers(request):
    # only allow POSTs
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    all_available_servers = Server.objects.filter(server_up=True)
    try:
        if len(all_available_servers) > 0:
            servers = dict()
            for s in all_available_servers:
                server = dict()
                server['localhostname'] = s.localhostname
                server['ipaddress'] = s.external_ip
                server['monitid'] = s.monit_id
                server['incarnation'] = s.last_data_received
                servers[s.monit_id] = server
        response = JsonResponse(servers, status=200)
    except StandardError as e:
        response = JsonResponse({'error': e.message, 'status': '500'}, status=500)
    return response
