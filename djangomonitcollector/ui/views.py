import datetime
import time
from pytz import timezone

from braces.views import LoginRequiredMixin

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.generic import DetailView, ListView, UpdateView, DeleteView
from django_filters.views import FilterView

from djangomonitcollector.datacollector.models import MemoryCPUSystemStats, MemoryCPUProcessStats
from djangomonitcollector.datacollector.models import Server, MonitEvent
from djangomonitcollector.users.models import validate_user, Settings
from djangomonitcollector.ui.models import HostGroup

from djangomonitcollector.ui.forms import SettingsForm
from filters import IntelliEventsFilter

# import the logging library
import logging
import pytz

# Get an instance of a logger
logger = logging.getLogger(__name__)

default_display_period = int(
    getattr(settings, 'DISPLAY_PERIOD', 1))  # four_hours


@user_passes_test(validate_user, login_url='/accounts/login/')
def dashboard(request):
    org = request.user.organisation

    servers = Server.objects.filter(
        organisation=org).order_by('host_group','localhostname')
    host_groups = HostGroup.objects.filter(owned_by=org)
    if org.server_set.all().count() > 0:
        for server in servers:
            server.alerts = server.monitevent_set.filter(is_active=True, is_ack=False).count()
            server.processes = len(set(server.process_set.all()))
        return render(request, 'ui/dashboard.html', {'servers': servers, 'host_groups': host_groups, 'server_found': True})
    else:
        return render(request, 'ui/dashboard.html', {'server_found': False})


@user_passes_test(validate_user, login_url='/accounts/login/')
def server(request, server_id):
    server = Server.objects.get(id=server_id)
    tz = timezone(server.data_timezone)
    now = datetime.datetime.now().replace(tzinfo=tz)
    display_time = datetime.timedelta(hours=default_display_period)
    min_display = now - display_time
    min_display = min_display.replace(tzinfo=tz)
    system = server.system
    system_resources = MemoryCPUSystemStats.objects.filter(
        date_last__gt=min_display,
        system_id=system
    ).order_by('-id').reverse()
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

    user_tz = timezone(request.user.user_timezone)
    print user_tz
    for resources_at_some_time in system_resources_list:
        adjusted_date_last = resources_at_some_time.date_last.astimezone(user_tz)
        date_last.append(str(
            time.mktime(adjusted_date_last.timetuple())))
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
    programs = server.program_set.all().order_by('name')
    files = server.file_set.all().order_by('name')
    directories = server.directory_set.all().order_by('name')
    nets = server.net_set.all().order_by('name')
    filesystems = server.filesystem_set.all().order_by('name')
    hosts = server.host_set.all().order_by('name')
    alerts_count = server.monitevent_set.filter(is_active=True).count()

    disk_usage = 0
    for fs in filesystems:
        if fs.name in ['__', '_', '___']:
            disk_usage = int(fs.blocks_percent_last)

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
        'programs': programs,
        'files': files,
        'directories': directories,
        'filesystems': filesystems,
        'disk_usage': disk_usage,
        'hosts': hosts,
        'alerts_count': alerts_count,
        'monit_update_period': server.monit_update_period,
        'monitoring_enabled': (server.disable_monitoring or server.user.settings.general_auto_add_unknown_servers)
    })

    # except Exception  as e:
    #     error_details = e.message
    # return render(request, 'ui/dashboard.html', {'server_found': False,
    # 'error': error_details})


@user_passes_test(validate_user, login_url='/accounts/login/')
def process(request, server_id, process_name):
    server = Server.objects.get(id=server_id)
    server_tz = pytz.timezone(server.data_timezone)
    utc_dt = datetime.datetime.utcnow()
    utc_dt = utc_dt.replace(tzinfo=timezone("UTC"))
    server_date_now = utc_dt.astimezone(server_tz)

    display_time = datetime.timedelta(hours=default_display_period)
    min_display = server_date_now - display_time

    process = server.process_set.get(name=process_name)

    process_resources = MemoryCPUProcessStats.objects.filter(
        date_last__gt=min_display,
        date_last__lt=server_date_now,
        process_id=process
    )
    process_resources_list = list(process_resources)

    date_last = []
    cpu_percent = []
    memory_percent = []
    memory_kilobyte = []

    user_tz = timezone(request.user.user_timezone)
    for resources_at_some_time in process_resources_list:
        adjusted_date_last = resources_at_some_time.date_last.astimezone(user_tz)
        date_last.append(str(
            time.mktime(adjusted_date_last.timetuple())))
        cpu_percent.append(resources_at_some_time.cpu_percent)
        memory_percent.append(resources_at_some_time.memory_percent)
        memory_kilobyte.append(resources_at_some_time.memory_kilobyte)

    date_last = "[{0}]".format(",".join(date_last))

    return render(request, 'ui/process.html',
                  {
                      'enable_buttons': False,
                      'process_found': True,
                      'server': server,
                      'process': process,
                      'date_last': date_last,
                      'cpu_percent': cpu_percent,
                      'memory_percent': memory_percent,
                      'memory_kilobyte': memory_kilobyte,
                      'monit_update_period': server.monit_update_period
                  }
                  )


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
    org = request.user.organisation
    host_groups = HostGroup.objects.filter(owned_by=org)
    servers = Server.objects.filter(
        organisation=org).order_by('host_group','localhostname')

    for server in servers:
        server.alerts = server.monitevent_set.filter(is_active=True, is_ack=False).count()
        server.processes = len(set(server.process_set.all()))
    table_html = render_to_string(
        'ui/includes/dashboard_table.html', {'servers': servers, 'host_groups': host_groups})
    return JsonResponse({'table_html': table_html})


def load_system_table(request, server_id):
    server = Server.objects.get(id=server_id)
    processes = server.process_set.all().order_by('name')
    table_html = render_to_string('ui/includes/server_table.html',
                                  {'server': server, 'processes': processes})
    return JsonResponse({'table_html': table_html})


def load_system_data(request, server_id):
    server = Server.objects.get(id=server_id)
    system = server.system
    processes = server.process_set.all().order_by('name')
    table_html = render_to_string('ui/includes/server_table.html',
                                  {'server': server, 'processes': processes})
    data = {'table_html': table_html,
            'date': system.date_last,
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


def load_process_table(request, server_id, process_name):
    server = Server.objects.get(id=server_id)
    process = server.process_set.get(name=process_name)
    table_html = render_to_string(
        'ui/includes/process_table.html', {'process': process})
    return JsonResponse({'table_html': table_html})


def load_process_data(request, server_id, process_name):
    server = Server.objects.get(id=server_id)
    process = server.process_set.get(name=process_name)
    system = server.system
    table_html = render_to_string(
        'ui/includes/process_table.html', {'process': process})

    data = {'date': system.date_last,
            'cpu_percenttotal': process.cpu_percent_last,
            'memory_percenttotal': process.memory_percent_last,
            'memory_kilobytetotal': process.memory_kilobyte_last,
            'table_html': table_html
            }
    return JsonResponse(data)

# Server


class ServerShowView(LoginRequiredMixin, DetailView):
    model = Server


class ServerDeleteView(LoginRequiredMixin, DeleteView):
    model = Server
    success_url = reverse_lazy('ui:dashboard')


class ServerUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['http_address',
              'http_username',
              'http_password',
              'monit_update_period',
              'data_timezone',
              'disable_monitoring'
              ]
    model = Server

    def get_success_url(self):
        server_id = self.kwargs['pk']
        return reverse("ui:server_show",
                       kwargs={"pk": server_id})


class SettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = Settings
    form_class = SettingsForm

    def get_success_url(self):
        settings_id = self.request.user.organisation.settings.id
        return reverse(
            "ui:settings_update",
            kwargs={
                "pk": settings_id
                }
                )


class EventListView(LoginRequiredMixin, ListView):
    model = MonitEvent

    def get_queryset(self):
        server_id = self.kwargs['pk']
        return self.model.objects.filter(
            server=server_id,
            is_active=True,
            is_ack=False
            ).order_by('-event_time')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(EventListView, self).get_context_data(**kwargs)

        server_id = self.kwargs['pk']
        server = Server.objects.get(id=int(server_id))
        context['server'] = server
        context['alerts_count'] = server.monitevent_set.filter(
            is_active=True, is_ack=False).count()
        return context


@user_passes_test(validate_user, login_url='/accounts/login/')
def configuration(request):
    return render(request, 'ui/settings.html')


def ack_event(request):
    event_id = request.POST['event_id']
    try:
        event = MonitEvent.objects.get(id=event_id)
        event.is_ack = True
        event.save()
        res = {
            'error_id': 0,
            'event_id': event_id
        }

    except StandardError as e:
        res = {
            'error': e.message,
            'error_id': 1
        }
    return JsonResponse(res)


def notifications(request):
    pass


class IntelliEvent(LoginRequiredMixin, FilterView):
    filterset_class = IntelliEventsFilter

