from xml.dom import minidom

from braces.views import LoginRequiredMixin

from django.conf import settings
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from djangomonitcollector.users.models import CollectorKey, Organisation
from django.views.generic import ListView, UpdateView, CreateView
from models.server import Server
from django.core.urlresolvers import reverse

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class OrganisationListView(LoginRequiredMixin, ListView):
    model = Organisation


class OrganisationUpdateView(LoginRequiredMixin, UpdateView):
    model = Organisation
    fields = '__all__'

    def get_success_url(self):
        return reverse('datacollector:organisations')


class OrganisationCreateView(LoginRequiredMixin, CreateView):
    model = Organisation
    fields = '__all__'

    def get_success_url(self):
        return reverse('datacollector:organisations')


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


def collect_data(xml_str, ck, ip_addr, host_group):
    try:
        xmldoc = minidom.parseString(xml_str)
        monit_id = xmldoc.getElementsByTagName(
            'monit')[0].attributes["id"].value
    except:
        return False, "Problem parsing the xml document"

    #  Check if we have many organisations
    multi_tenant = settings.ENABLE_MULTI_TENANT
    # try:
    if multi_tenant:
        try:
            ckobj = CollectorKey.objects.get(pk=ck)
        except CollectorKey.DoesNotExist:
            raise CollectorKeyError("No Such Key Error {0}".format(ck))
        except ValueError:
            raise CollectorKeyError("Wrong Key Format {0}".format(ck))

        if ckobj:
            if ckobj.is_enabled:
                Server.update(
                    xmldoc,
                    monit_id,
                    ckobj.organisation,
                    ip_addr,
                    host_group
                )
            else:
                raise CollectorKeyError("Key Not Active {0}".format(ck))
        else:
            raise CollectorKeyError("No Such Key Error {0}".format(ck))

    else:

        default_org = Organisation.getdefault()
        Server.update(
            xmldoc,
            monit_id,
            default_org,
            ip_addr,
            host_group
        )

    return True, "OK"



#  API Calls

'''
Entry point for the collector
'''
@csrf_exempt
def collector(request, collector_key, host_group=None):

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = request.body
    ip_addr = get_client_ip(request)

    try:
        collected, status = collect_data(data, collector_key, ip_addr, host_group)
    except CollectorKeyError as e:
        collected = False
        status = e.message
    if not collected:
        response = JsonResponse(
            {
                'error': status,
                'status': '400'
            },
            status=400)

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
                server['org_id'] = s.organisation.id
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


@csrf_exempt
def delete_server(request, url_params):

    if request.method != 'DELETE':
        return HttpResponseNotAllowed(['DELETE'])

    res = dict()
    try:
        slug = url_params
        server = Server.objects.get(localhostname=slug)
        server.delete()
        res['status'] = "OK"
        res['status_details'] = None
        res['http_status_code'] = 200
    except Server.DoesNotExist as e:
        res['status'] = "Not Found"
        res['status_details'] = "{}".format(e)
        res['http_status_code'] = 404
    except StandardError as e:
        res['status'] = "Error"
        res['status_details'] = "{}".format(e)
        res['http_status_code'] = 500

    return JsonResponse(res, status=res['http_status_code'])
