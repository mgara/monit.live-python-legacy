import time
import datetime

from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.conf import settings
import requests
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from braces.views import LoginRequiredMixin

from pytz import timezone
import pytz

from djangomonitcollector.datacollector.models import  Server
from djangomonitcollector.datacollector.models import MemoryCPUSystemStats
from djangomonitcollector.users.models import validate_user


# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

monit_update_period = getattr(settings, 'MONIT_UPDATE_PERIOD', 60)
enable_buttons = getattr(settings, 'ENABLE_BUTTONS', False)
monit_user = getattr(settings, 'MONIT_USER', "")
monit_password = getattr(settings, 'MONIT_PASSWORD', "")
monit_port = str(getattr(settings, 'MONIT_PORT', 2812))
default_display_period = int(getattr(settings, 'DISPLAY_PERIOD', 4))  # four_hours


@user_passes_test(validate_user, login_url='/accounts/login/')
def dashboard(request):
    if Server.objects.all().count() > 0:
        servers = Server.objects.all().order_by('localhostname')
        return render(request, 'ui/dashboard.html', {'servers': servers, 'server_found': True})
    else:
        return render(request, 'ui/dashboard.html', {'server_found': False})


@user_passes_test(validate_user, login_url='/accounts/login/')
def server(request, server_id):
    page_header = "test"
    tz = timezone('US/Eastern')
    now = datetime.datetime.now().replace(tzinfo=tz)
    display_time = datetime.timedelta(hours=default_display_period)
    min_display = now - display_time
    min_display = min_display.replace(tzinfo=tz)

    server = Server.objects.get(id=server_id)
    system = server.system
    system_resources = MemoryCPUSystemStats.objects.filter(
        date_last__gt=min_display,
        date_last__lt=now,
        system_id=system
    )
    system_resources_list = list(system_resources)

    date_last = []
    load_avg01 = []
    load_avg05 = []
    load_avg15 = []
    cpu_user = []
    cpu_system = []
    cpu_wait = []
    memory_percent = []
    memory_kilobyte = []
    swap_percent = []
    swap_kilobyte = []

    for resources_at_some_time in system_resources_list:
        date_last.append(str(time.mktime(resources_at_some_time.date_last.replace(tzinfo=None).timetuple())))
        load_avg01.append(resources_at_some_time.load_avg01)
        load_avg05.append(resources_at_some_time.load_avg05)
        load_avg15.append(resources_at_some_time.load_avg15)
        cpu_user.append(resources_at_some_time.cpu_user)
        cpu_system.append(resources_at_some_time.cpu_system)
        cpu_wait.append(resources_at_some_time.cpu_wait)
        memory_percent.append(resources_at_some_time.memory_percent)
        memory_kilobyte.append(resources_at_some_time.memory_kilobyte)
        swap_percent.append(resources_at_some_time.swap_percent)
        swap_kilobyte.append(resources_at_some_time.swap_kilobyte)

    date_last = "[{0}]".format(",".join(date_last))

    processes = server.process_set.all().order_by('name')
    nets = server.net_set.all().order_by('name')

    return render(request, 'ui/server.html', {
        'server_found': True,
        'server': server,
        'system': system,
        'date_last': date_last,
        'load_avg01': load_avg01,
        'load_avg05': load_avg05,
        'load_avg15': load_avg15,
        'cpu_user': cpu_user,
        'cpu_system': cpu_system,
        'cpu_wait': cpu_wait,
        'memory_percent': memory_percent,
        'memory_kilobyte': memory_kilobyte,
        'swap_percent': swap_percent,
        'swap_kilobyte': swap_kilobyte,
        'processes': processes,
        'nets': nets,
        'monit_update_period': monit_update_period,
        'pageheader': page_header,
    })

    # except Exception  as e:
    #     error_details = e.message
    #     return render(request, 'ui/dashboard.html', {'server_found': False, 'error': error_details})


@user_passes_test(validate_user, login_url='/accounts/login/')
def process(request, server_id, process_name):
    try:
        server = Server.objects.get(id=server_id)
        process = server.process_set.get(name=process_name)
        return render(request, 'ui/process.html',
                      {'enable_buttons': False, 'process_found': True, 'server': server, 'process': process,
                       'monit_update_period': monit_update_period})
    except:
        return render(request, 'ui/process.html', {'process_found': False})


@user_passes_test(validate_user, login_url='/accounts/login/')
def process_action(request, server_id):
    if not request.POST:
        return HttpResponseNotAllowed(['POST'])
    action = request.POST['action']
    process_name = request.POST['process']
    server = Server.objects.get(id=server_id)
    process = server.process_set.get(name=process_name)
    ip_address = server.address
    time_out = 15
    try:
        # would only work for this server
        # subprocess.call(["monit", action, process_name])

        monit_url = 'http://%s:%s@%s:%s/%s' % (monit_user, monit_password, ip_address, monit_port, process_name)
        requests.post(monit_url, {'action': action}, timeout=time_out)
        action_labels = {'start': 'starting...', 'stop': 'stopping...', 'restart': 'restarting...',
                         'unmonitor': 'disable monitoring...', 'monitor': 'enable monitoring...'}
        if action in action_labels:
            process.status = action_labels.get(action)
            if action == 'unmonitor':
                process.monitor = 0
            elif action == 'monitor':
                process.monitor = 2
            process.save()
        return redirect(
            reverse('ui.views.process', kwargs={'server_id': server.id, 'process_name': process_name}))
    except:
        return render(request, 'ui/error.html',
                      {'time_out': time_out, 'monit_user': monit_user, 'ip_address': ip_address,
                       'monit_port': monit_port, 'process_name': process_name})


@user_passes_test(validate_user, login_url='/accounts/login/')
def confirm_delete(request, server_id):
    server = Server.objects.get(id=server_id)
    return render(request, "ui/confirm_delete.html", {"server": server})


@user_passes_test(validate_user, login_url='/accounts/login/')
def delete_server(request, server_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    server = Server.objects.get(id=server_id)
    server.delete()
    return redirect(reverse('ui.views.dashboard'))


# Ajax Views
def load_dashboard_table(request):
    servers = Server.objects.all().order_by('localhostname')
    table_html = render_to_string('ui/includes/dashboard_table.html', {'servers': servers})
    return JsonResponse({'table_html': table_html})


def load_system_table(request, server_id):
    server = Server.objects.get(id=server_id)
    processes = server.process_set.all().order_by('name')
    table_html = render_to_string('ui/includes/server_table.html',
                                  {'server': server, 'processes': processes})
    return JsonResponse({'table_html': table_html})


def load_process_table(request, server_id, process_name):
    server = Server.objects.get(id=server_id)
    process = server.process_set.get(name=process_name)
    table_html = render_to_string('ui/includes/process_table.html', {'process': process})
    return JsonResponse({'table_html': table_html})


def load_system_data(request, server_id):
    server = Server.objects.get(id=server_id)
    system = server.system
    processes = server.process_set.all().order_by('name')
    table_html = render_to_string('ui/includes/server_table.html',
                                  {'server': server, 'processes': processes})
    data = {'table_html': table_html,
            'date': datetime.datetime.fromtimestamp(system.date_last).replace(tzinfo=pytz.timezone("US/Eastern")),
            'load_avg01': system.load_avg01_last,
            'load_avg05': system.load_avg05_last,
            'load_avg15': system.load_avg15_last,
            'cpu_user': system.cpu_user_last,
            'cpu_system': system.cpu_system_last,
            'cpu_wait': system.cpu_wait_last,
            'memory_percent': system.memory_percent_last,
            'memory_kilobyte': system.memory_kilobyte_last,
            'swap_percent': system.swap_percent_last,
            'swap_kilobyte': system.swap_kilobyte_last}
    return JsonResponse(data)


def load_process_data(request, server_id, process_name):
    server = Server.objects.get(id=server_id)
    process = server.process_set.get(name=process_name)
    table_html = render_to_string('ui/includes/process_table.html', {'process': process})
    data = {'date': process.date_last, 'cpu_percenttotal': process.cpu_percenttotal_last,
            'memory_percenttotal': process.memory_percenttotal_last,
            'memory_kilobytetotal': process.memory_kilobytetotal_last}
    return JsonResponse(data)


class ServerShowView(LoginRequiredMixin, DetailView):
    model = Server


class ServerUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['http_address', 'http_username', 'http_password','monit_update_period','data_timezone','is_new']
    model = Server

    def get_success_url(self):
        server_id = self.kwargs['pk']
        return reverse("ui:server_show",
                       kwargs={"pk": server_id})

