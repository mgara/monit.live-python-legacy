import datetime
import ast
from pytz import timezone

from braces.views import LoginRequiredMixin
from urlparse import urlparse
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

from djangomonitcollector.datacollector.models import Server, MonitEvent
from djangomonitcollector.users.models import validate_user, Settings
from djangomonitcollector.users.models import HostGroup

from djangomonitcollector.ui.forms import SettingsForm
from filters import IntelliEventsFilter

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

default_display_period = int(
    getattr(settings, 'DISPLAY_PERIOD', 1))  # four_hours


@user_passes_test(validate_user, login_url='/accounts/login/')
def dashboard(request):
    org = request.user.organisation
    hgs = request.user.host_groups.all()
    all_hgs = HostGroup.objects.filter(owned_by=org)
    org_has_hgs = True if len(all_hgs) > 0 else False
    user_has_hgs = True if len(hgs) > 0 else False

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
            'org_has_hgs': org_has_hgs,
            'user_has_hgs': user_has_hgs,
            'servers': servers,
            'hgs': hgs,
            'all_hgs': all_hgs,
            'server_found': server_found
        }
    )


@user_passes_test(validate_user, login_url='/accounts/login/')
def server(request, server_id):
    server = Server.objects.get(pk=server_id)
    system = server.system

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
        if fs.display_name == '/':
            if fs.blocks_percent_last:
                disk_usage = int(fs.blocks_percent_last)

    return render(request, 'ui/server.html', {
        'server_found': True,
        'server': server,
        'system': system,
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


@user_passes_test(validate_user, login_url='/accounts/login/')
def process(request, server_id, process_name):
    server = Server.objects.get(id=server_id)
    process = server.process_set.get(name=process_name)

    return render(request, 'ui/process.html',
                  {
                      'enable_buttons': False,
                      'process_found': True,
                      'server': server,
                      'process': process,
                      'monit_update_period': server.monit_update_period
                  }
                  )


@user_passes_test(validate_user, login_url='/accounts/login/')
def filesystem(request, server_id, filesystem_id):
    server = Server.objects.get(id=server_id)
    filesystem = server.filesystem_set.get(pk=filesystem_id)

    return render(request, 'ui/filesystem.html',
                  {
                      'enable_buttons': False,
                      'process_found': True,
                      'server': server,
                      'process': filesystem,
                      'monit_update_period': server.monit_update_period
                  }
                  )


@user_passes_test(validate_user, login_url='/accounts/login/')
def network(request, server_id, network_name):
    server = Server.objects.get(id=server_id)
    network = server.net_set.get(name=network_name)

    return render(request, 'ui/network.html',
                  {
                      'enable_buttons': False,
                      'process_found': True,
                      'server': server,
                      'net': network,
                      'monit_update_period': server.monit_update_period
                  }
                  )


def load_dashboard_table(request):
    org = request.user.organisation
    hgs = request.user.host_groups.all()
    all_hgs = HostGroup.objects.filter(owned_by=org)
    org_has_hgs = True if len(all_hgs) > 0 else False
    user_has_hgs = True if len(hgs) > 0 else False

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
            'org_has_hgs': org_has_hgs,
            'user_has_hgs': user_has_hgs,
            'servers': servers,
            'hgs': hgs,
            'server_found': server_found
        }
    )
    return JsonResponse({'table_html': table_html})



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

    def get_context_data(self, **kwargs):
        o = urlparse(self.request.build_absolute_uri())
        context = super(SettingsUpdateView, self).get_context_data(**kwargs)
        context['scheme'] = o.scheme
        context['port'] = o.port
        context['base_url'] = "{}://{}".format(o.scheme, o.netloc)

        return context

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
        server = Server.objects.get(id=server_id)
        context['server'] = server
        context['alerts_count'] = server.monitevent_set.filter(
            is_active=True, is_ack=False).count()
        return context


#   Ajax call
#   This is called when you click on the acknowledge button in the server
#   events page.
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


#  Ajax call
#  Update user hostgroups from the dashboard call
def update_user_hgs(request):
    org = request.user.organisation
    current_user = request.user
    hgs = request.POST['user_hgs']
    all_gs = HostGroup.objects.filter(owned_by=org)
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
