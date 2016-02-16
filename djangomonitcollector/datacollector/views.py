from xml.dom import minidom

from django.conf import settings
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from djangomonitcollector.users.models import CollectorKey
from djangomonitcollector.users.models import User
from models.server import Server

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class CollectorKeyError(Exception):
    def __init__(self, message):
        self.message = message


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def collect_data(xml_str, ck, ip_addr):
    try:
        xmldoc = minidom.parseString(xml_str)
        monit_id = xmldoc.getElementsByTagName(
                'monit')[0].attributes["id"].value
    except:
        return False, "Problem parsing the xml document"

    multi_tenant = settings.ENABLE_MULTI_TENANT
    manual_approval_required = settings.ENABLE_MANUAL_APPROVAL

    # try:
    if multi_tenant:
        ckobj = CollectorKey.objects.get(pk=ck)
        if ckobj:
            if ckobj.is_enabled:
                Server.update(
                        xmldoc,
                        monit_id,
                        ckobj.user_id,
                        ip_addr,
                        manual_approval_required
                )
            else:
                raise CollectorKeyError("Key Not Active {0}".format(ck))
        else:
            raise CollectorKeyError("No Such Key Error {0}".format(ck))
    else:
        default_user = User.objects.all()[0]  # first user
        Server.update(
                xmldoc,
                monit_id,
                default_user,
                ip_addr,
                manual_approval_required
        )
    return True, "Toto"
    # except StandardError as e:
    #    return False, "Error While updating the server instance: {0}".format(e.message)
    # return True, "Server instance Updated"


@csrf_exempt
def collector(request, collector_key):
    # only allow POSTs
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    data = request.body
    ip_addr = get_client_ip(request)
    collected, status = collect_data(data, collector_key, ip_addr)
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
                server['monit_update_period'] = s.monit_update_period
                servers[s.monit_id] = server
        response = JsonResponse(servers, status=200)
    except StandardError as e:
        response = JsonResponse(
                {
                    'error': e.message,
                    'status': '500'
                },
                status=500
        )
    return response
