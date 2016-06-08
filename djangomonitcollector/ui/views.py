import datetime
import time
import ast
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
from django.views.generic import DetailView, ListView, UpdateView, DeleteView, CreateView
from django_filters.views import FilterView

from djangomonitcollector.datacollector.models import MemoryCPUSystemStats, MemoryCPUProcessStats
from djangomonitcollector.datacollector.models import FsAndDiskUsageStats, NetStats, Net
from djangomonitcollector.datacollector.models import Server, MonitEvent, AggregationPeriod
from djangomonitcollector.users.models import validate_user, Settings
from djangomonitcollector.users.models import HostGroup

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
    hgs = request.user.host_groups.all()
    all_hgs = HostGroup.objects.all()

    servers = []

    for hg in hgs:
        s = Server.objects.filter(
            organisation=org, host_group=hg).order_by(
                'localhostname'
        )
        list_of_servers = list(s)
        for s in list_of_servers:
            servers.append(s)

    server_found = False
    for server in servers:
        server.alerts = server.monitevent_set.filter(
            is_active=True, is_ack=False).count()
        server.processes = len(set(server.process_set.all()))
        server_found = True

    return render(
        request,
        'ui/dashboard.html',
        {
            'servers': servers,
            'hgs': hgs,
            'all_hgs': all_hgs,
            'server_found': server_found
        }
    )


@user_passes_test(validate_user, login_url='/accounts/login/')
def server(request, server_id):
    server = Server.objects.get(pk=server_id)
    user_tz = timezone(request.user.user_timezone)
    server_tz = pytz.timezone(server.data_timezone)
    utc_dt = datetime.datetime.utcnow()
    utc_dt = utc_dt.replace(tzinfo=timezone("UTC"))
    server_date_now = utc_dt.astimezone(server_tz)

    display_time = datetime.timedelta(minutes=10)
    min_display = server_date_now - display_time

    system = server.system

    system_resources = MemoryCPUSystemStats.objects.filter(
        date_last__gt=min_display,
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

    user_tz = timezone(request.user.user_timezone)
    for resources_at_some_time in system_resources_list:
        adjusted_date_last = resources_at_some_time.date_last.astimezone(
            user_tz)
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
    alerts_count = server.monitevent_set.filter(
        is_active=True, is_ack=False).count()

    disk_usage = 0
    for fs in filesystems:
        if fs.name in ['__', '_', '___']:
            if fs.blocks_percent_last:
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
        adjusted_date_last = resources_at_some_time.date_last.astimezone(
            user_tz)
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
def filesystem(request, server_id, filesystem_id):
    server = Server.objects.get(id=server_id)
    server_tz = pytz.timezone(server.data_timezone)
    utc_dt = datetime.datetime.utcnow()
    utc_dt = utc_dt.replace(tzinfo=timezone("UTC"))
    server_date_now = utc_dt.astimezone(server_tz)

    display_time = datetime.timedelta(hours=default_display_period)
    min_display = server_date_now - display_time

    filesystem = server.filesystem_set.get(pk=filesystem_id)

    filesystem_history = FsAndDiskUsageStats.objects.filter(
        date_last__gt=min_display,
        date_last__lt=server_date_now,
        fs_id=filesystem
    )
    filesystem_resources_list = list(filesystem_history)

    date_last = []
    blocks_percent = []
    blocks_usage = []
    inode_percent = []
    inode_usage = []

    user_tz = timezone(request.user.user_timezone)
    for resources_at_some_time in filesystem_resources_list:
        adjusted_date_last = resources_at_some_time.date_last.astimezone(
            user_tz)
        date_last.append(str(
            time.mktime(adjusted_date_last.timetuple())))
        blocks_percent.append(resources_at_some_time.blocks_percent)
        blocks_usage.append(resources_at_some_time.blocks_usage)
        inode_percent.append(resources_at_some_time.inode_percent)
        inode_usage.append(resources_at_some_time.inode_usage)

    date_last = "[{0}]".format(",".join(date_last))

    return render(request, 'ui/filesystem.html',
                  {
                      'enable_buttons': False,
                      'process_found': True,
                      'server': server,
                      'process': process,
                      'date_last': date_last,
                      'blocks_percent': blocks_percent,
                      'blocks_usage': blocks_usage,
                      'inode_percent': inode_percent,
                      'inode_usage': inode_usage,
                      'monit_update_period': server.monit_update_period
                  }
                  )


@user_passes_test(validate_user, login_url='/accounts/login/')
def network(request, server_id, network_name):
    server = Server.objects.get(id=server_id)
    server_tz = pytz.timezone(server.data_timezone)
    utc_dt = datetime.datetime.utcnow()
    utc_dt = utc_dt.replace(tzinfo=timezone("UTC"))
    server_date_now = utc_dt.astimezone(server_tz)

    display_time = datetime.timedelta(hours=default_display_period)
    min_display = server_date_now - display_time

    network = server.net_set.get(name=network_name)

    network_history = NetStats.objects.filter(
        date_last__gt=min_display,
        date_last__lt=server_date_now,
        net_id=network
    )
    netowkr_resources_list = list(network_history)

    date_last = []
    download_packet = []
    download_bytes = []
    download_errors = []

    upload_packet = []
    upload_bytes = []
    upload_errors = []

    user_tz = timezone(request.user.user_timezone)
    for resources_at_some_time in netowkr_resources_list:
        adjusted_date_last = resources_at_some_time.date_last.astimezone(
            user_tz)
        date_last.append(str(
            time.mktime(adjusted_date_last.timetuple())))
        download_packet.append(resources_at_some_time.download_packet)
        download_bytes.append(resources_at_some_time.download_bytes)
        download_errors.append(resources_at_some_time.download_errors)

        upload_packet.append(resources_at_some_time.upload_packet)
        upload_bytes.append(resources_at_some_time.upload_bytes)
        upload_errors.append(resources_at_some_time.upload_errors)

    date_last = "[{0}]".format(",".join(date_last))

    return render(request, 'ui/network.html',
                  {
                      'enable_buttons': False,
                      'process_found': True,
                      'server': server,
                      'net': network,
                      'date_last': date_last,
                      'download_packet': download_packet,
                      'download_bytes': download_bytes,
                      'download_errors': download_errors,
                      'upload_packet': upload_packet,
                      'upload_bytes': upload_bytes,
                      'upload_errors': upload_errors,
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


def load_dashboard_table(request):
    org = request.user.organisation
    hgs = request.user.host_groups.all()
    servers = []

    for hg in hgs:
        s = Server.objects.filter(
            organisation=org, host_group=hg).order_by(
                'localhostname'
        )
        list_of_servers = list(s)
        for s in list_of_servers:
            servers.append(s)

    server_found = False
    for server in servers:
        server.alerts = server.monitevent_set.filter(
            is_active=True, is_ack=False).count()
        server.processes = len(set(server.process_set.all()))
        server_found = True

    table_html = render_to_string(
        'ui/includes/dashboard_table.html', {
            'servers': servers,
            'hgs': hgs,
            'server_found': server_found
        }
    )
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


def load_network_data(request, server_id, net_name):
    server = Server.objects.get(id=server_id)
    net = server.net_set.get(name=net_name)

    table_html = render_to_string(
        'ui/includes/net_table.html', {'net': net})

    data = {'date': net.date_last,
            'download_packet_sum': net.download_packet_sum,
            'download_bytes_sum': net.download_bytes_sum,
            'download_errors_sum': net.download_errors_sum,
            'upload_packet_sum': net.download_packet_sum,
            'upload_bytes_sum': net.download_bytes_sum,
            'upload_errors_sum': net.download_errors_sum,
            'table_html': table_html
            }
    return JsonResponse(data)


class AggreationView(LoginRequiredMixin, ListView):
    model = AggregationPeriod


class AggreationCreate(LoginRequiredMixin, CreateView):
    model = AggregationPeriod
    fields = '__all__'


class AggreationUpdate(LoginRequiredMixin, UpdateView):
    model = AggregationPeriod
    fields = '__all__'


class AggreationDelete(LoginRequiredMixin, DeleteView):
    model = AggregationPeriod
    success_url = reverse_lazy('ui:aggregation')


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


#  ajax call
# this is called when you click on the acknowledge button in the server
# events page.
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


#  ajax call
#  Update user hostgroups from the dashboard call
def update_user_hgs(request):
    current_user = request.user
    hgs = request.POST['user_hgs']
    all_gs = HostGroup.objects.all()
    try:
        select_hgs = ast.literal_eval(hgs)
        selected_hgs_count = len(select_hgs)

        if selected_hgs_count > 0:
            current_user.host_groups.clear()
            for hg in select_hgs:
                host_group = HostGroup.objects.get(slug=hg)
                current_user.host_groups.add(host_group)
            current_user.save()
        else:
            current_user.host_groups.clear()
            for hg in all_gs:
                current_user.host_groups.add(hg)
            current_user.save()
        res = {
            'status': 200
        }
    except StandardError as e:
        res = {
            'status': 500,
            'error': e.message
        }

    return JsonResponse(res)


def notifications(request):
    pass


class IntelliEvent(LoginRequiredMixin, FilterView):
    filterset_class = IntelliEventsFilter


def get_hours_from_period(p):
    periods = {
        '1h': 1,
        '3h': 3,
        '1d': 24,
        '3d': 24*3,
        '1w': 24*7,
        '1m': 24*7,
        '1m': 24*30,
        '3m': 24*30*3,
        '6m': 24*30*6,
        '1y': 24*365,
        'max': 24*365*5,
    }

    return periods[p]


def set_stats_period(request):
    try:
        p = request.POST['period']
        if p:
            request.session['period'] = p
        res = {
            'status': 200
        }
    except StandardError as e:
        res = {
            'status': 500,
            'error': e.message
        }
    return JsonResponse(res)


def get_network_usage(request, pk):
    try:
        server = Server.objects.get(id=pk)
        period = request.session.get('period', '1d')
        hrs = get_hours_from_period(period)
        user_tz = timezone(request.user.user_timezone)
        server_tz = pytz.timezone(server.data_timezone)
        utc_dt = datetime.datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=timezone("UTC"))
        server_date_now = utc_dt.astimezone(server_tz)

        display_time = datetime.timedelta(hours=hrs)
        min_display = server_date_now - display_time

        all_nics = server.net_set.all()
        t = dict()
        for nic in all_nics:
            t[nic.name] = get_network_usage_for_period(
                nic, user_tz, min_display, server_date_now)

        res = {
            'status': 200,
            'res': t
        }
    except StandardError as e:
        res = {
            'status': 500,
            'error': e.message
        }
    return JsonResponse(res)


def get_filesystem_usage(request, pk):

    try:
        server = Server.objects.get(id=pk)
        period = request.session.get('period', '1d')
        hrs = get_hours_from_period(period)
        user_tz = timezone(request.user.user_timezone)

        server_tz = pytz.timezone(server.data_timezone)
        utc_dt = datetime.datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=timezone("UTC"))
        server_date_now = utc_dt.astimezone(server_tz)

        display_time = datetime.timedelta(hours=hrs)
        min_display = server_date_now - display_time

        all_fs = server.filesystem_set.all()
        t = dict()
        for fs in all_fs:
            t[fs.name] = get_filesystem_usage_for_period(
                fs, user_tz, min_display, server_date_now)

        res = {
            'status': 200,
            'res': t
        }
    except StandardError as e:
        res = {
            'status': 500,
            'error': e.message
        }
    return JsonResponse(res)


def get_filesystem_usage_for_period(fs, user_tz, min_display, max_display):

    filesystem_history = FsAndDiskUsageStats.objects.filter(
        date_last__gt=min_display,
        date_last__lt=max_display,
        fs_id=fs
    ).order_by('id')
    filesystem_resources_list = list(filesystem_history)

    date_last = []
    blocks_percent = []
    blocks_usage = []
    inode_percent = []
    inode_usage = []
    for resources_at_some_time in filesystem_resources_list:
        adjusted_date_last = resources_at_some_time.date_last.astimezone(
            user_tz)
        date_last.append(str(
            time.mktime(adjusted_date_last.timetuple())))
        blocks_percent.append(resources_at_some_time.blocks_percent)
        blocks_usage.append(resources_at_some_time.blocks_usage)
        inode_percent.append(resources_at_some_time.inode_percent)
        inode_usage.append(resources_at_some_time.inode_usage)

    date_last = "[{0}]".format(",".join(date_last))

    return date_last, blocks_percent, blocks_usage, inode_percent, inode_usage


def get_network_usage_for_period(nic, user_tz, min_display, max_display):

    network_history = NetStats.objects.filter(
        date_last__gt=min_display,
        date_last__lt=max_display,
        net_id=nic
    ).order_by('id')

    netowkr_resources_list = list(network_history)

    date_last = []
    download_packet = []
    download_bytes = []
    download_errors = []

    upload_packet = []
    upload_bytes = []
    upload_errors = []

    for resources_at_some_time in netowkr_resources_list:
        adjusted_date_last = resources_at_some_time.date_last.astimezone(
            user_tz)
        date_last.append(str(
            time.mktime(adjusted_date_last.timetuple())))
        download_packet.append(resources_at_some_time.download_packet)
        download_bytes.append(resources_at_some_time.download_bytes)
        download_errors.append(resources_at_some_time.download_errors)

        upload_packet.append(resources_at_some_time.upload_packet)
        upload_bytes.append(resources_at_some_time.upload_bytes)
        upload_errors.append(resources_at_some_time.upload_errors)

    date_last = "[{0}]".format(",".join(date_last))

    return date_last, download_packet, download_bytes, download_errors, upload_packet, upload_bytes, upload_errors


def get_system_usage(request, pk):

    try:

        server = Server.objects.get(id=pk)
        period = request.session.get('period', '1d')
        hrs = get_hours_from_period(period)
        user_tz = timezone(request.user.user_timezone)

        server_tz = pytz.timezone(server.data_timezone)
        utc_dt = datetime.datetime.utcnow()
        utc_dt = utc_dt.replace(tzinfo=timezone("UTC"))
        server_date_now = utc_dt.astimezone(server_tz)

        display_time = datetime.timedelta(hours=hrs)
        min_display = server_date_now - display_time

        system = server.system
        system_resources = MemoryCPUSystemStats.objects.filter(
            date_last__gt=min_display,
            system_id=system
        ).order_by('id')
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
        for resources_at_some_time in system_resources_list:
            adjusted_date_last = resources_at_some_time.date_last.astimezone(
                user_tz)
            date_last.append(
                time.mktime(adjusted_date_last.timetuple()))
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

        t = (date_last,
             load_avg01,
             load_avg05,
             load_avg15,
             cpu_user,
             cpu_system,
             cpu_wait,
             memory_percent,
             memory_kilobyte,
             swap_percent,
             swap_kilobyte)

        res = {
            'status': 200,
            'res': t
        }
    except StandardError as e:
        res = {
            'status': 500,
            'error': e.message
        }
    return JsonResponse(res)


def get_last_events(request):
    org = request.user.organisation
    pass


def serverkpis(request, pk):
    server = Server.objects.get(id=pk)
    tz = timezone(server.data_timezone)
    now = datetime.datetime.now().replace(tzinfo=tz)

    period = request.session.get('period', '1d')
    hrs = get_hours_from_period(period)

    display_time = datetime.timedelta(hours=hrs)
    min_display = now - display_time
    min_display = min_display.replace(tzinfo=tz)
    system = server.system

    alerts_count = server.monitevent_set.filter(
        is_active=True, is_ack=False).count()

    return render(request, 'ui/kpis.html', {
        'server_found': True,
        'server': server,
        'system': system,
        'alerts_count': alerts_count,
        'monit_update_period': server.monit_update_period,
        'monitoring_enabled': (server.disable_monitoring or server.user.settings.general_auto_add_unknown_servers)
    })
