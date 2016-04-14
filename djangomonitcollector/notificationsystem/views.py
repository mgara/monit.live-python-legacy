import ast
import re

from braces.views import LoginRequiredMixin
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from djangomonitcollector.datacollector.models import Server, MonitEvent
from forms import NotificationTypeForm, get_class_name_and_extra_params
from models import NotificationType
from django.contrib import messages


def check_item(item, string_list_of_items):
    if not string_list_of_items.strip():
        return True
    try:
        list_of_items = ast.literal_eval(string_list_of_items)
    except StandardError as e:
        print "exception while parsing {} ".format(string_list_of_items)
        print "exception details {}".format(e)
        return "Error"
    if len(list_of_items) == 0:
        return True
    if list_of_items is not None:
        if str(item) in list_of_items:
            return True
        return False
    return True


def notificationtypeactivation(request, pk):
    nt = NotificationType.objects.get(id=pk)
    if nt.notification_enabled:
        nt.notification_enabled = False
    else:
        nt.notification_enabled = True
    nt.save()
    return redirect('n:notificationtype_view', pk=pk)


def notificationtype_mute_all(request, pk):
    nt = NotificationType.objects.get(id=pk)

    #  TODO: im muting everything almost ....
    for event_object in MonitEvent.objects.filter(is_ack=False):
        if nt.notification_enabled:
            name_matches = check_item(
                    event_object.service.name, nt.notification_service)
            state_matches = check_item(
                    event_object.event_state, nt.notification_state)
            action_matches = check_item(
                    event_object.event_action, nt.notification_action)
            type_matches = check_item(
                    event_object.event_type, nt.notification_type)
            messages_matches = True if re.search(
                    nt.notification_message, event_object.event_message) else False

        if name_matches and state_matches and action_matches and type_matches and messages_matches:
            MonitEvent.mute(event_object)

    return redirect('n:notificationtype_view', pk=pk)


def get_user_services(org):
    '''
    This function returns the list of the services assigned to the current user
    '''

    user_servers = Server.objects.filter(organisation=org)
    service_list = tuple()

    items = list()

    for server in user_servers:
        items += server.process_set.all().order_by('name')
        items += server.program_set.all().order_by('name')
        items += server.file_set.all().order_by('name')
        items += server.net_set.all().order_by('name')
        items += server.filesystem_set.all().order_by('name')
        items += server.host_set.all().order_by('name')
        items.append(server.system)

    items = (i.name for i in items)  # get the name only
    items = list(set(items))  # remove duplicates
    service_list += tuple((i, i) for i in items)  # create final tuple
    return service_list


class NotificationTypeView(LoginRequiredMixin, DetailView):
    model = NotificationType
    fields = [
        'notification_server',
        'notification_service',
        'notification_type',
        'notification_state',
        'notification_action',
        'notification_message'
    ]

    def get_object(self):
        notification_type_id = self.kwargs['pk']
        return NotificationType.objects.get(id=notification_type_id)


class NotificationTypeCreate(LoginRequiredMixin, CreateView):
    form_class = NotificationTypeForm
    model = NotificationType

    def form_valid(self, form):
        form.instance.organisation = self.request.user.organisation

        return super(NotificationTypeCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
                NotificationTypeCreate, self).get_context_data(**kwargs)
        context['form'].fields['notification_user'] = forms.CharField(widget=forms.HiddenInput(),
                                                                      initial=self.request.user.id
                                                                      )
        context['form'].fields['notification_service'] = forms.MultipleChoiceField(widget=forms.SelectMultiple(),
                                                                                   choices=get_user_services(
                                                                                           self.request.user.organisation),
                                                                                   required=False
                                                                                   )
        return context


class NotificationTypeUpdate(LoginRequiredMixin, UpdateView):
    model = NotificationType
    form_class = NotificationTypeForm


    def get_context_data(self, **kwargs):
        context = super(
                NotificationTypeUpdate, self).get_context_data(**kwargs)
        context['form'].fields['notification_user'] = forms.CharField(widget=forms.HiddenInput(),
                                                                      initial=self.request.user.id
                                                                      )
        context['form'].fields['object_id'] = forms.CharField(widget=forms.HiddenInput(),
                                                              initial=self.object.id
                                                              )
        context['form'].fields['notification_service'] = forms.MultipleChoiceField(widget=forms.SelectMultiple(),
                                                                                   choices=get_user_services(
                                                                                           self.request.user.organisation)
                                                                                   )
        return context


class NotificationTypeDelete(DeleteView):
    model = NotificationType
    success_url = reverse_lazy('n:notificationtype_list')


class NotificationTypeListView(LoginRequiredMixin, ListView):
    model = NotificationType

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(NotificationTypeListView, self).get_context_data(**kwargs)

        if len(NotificationType.objects.all())==0:  # double check this filter.
            message = "No Configured Notifications Yet :)"
            messages.add_message(self.request, messages.INFO, message)

        return context

    def get_queryset(self):
        org = self.request.user.organisation

        return self.model.objects.filter(organisation=org)


def get_notification_plugin_form(request):
    try:
        is_update_form = 'notification_type_id' in request.GET
        plugin_name = request.GET['plugin_name']
        if is_update_form:
            notification_type_id = request.GET['notification_type_id']
            if notification_type_id.strip():
                extra_params_values = ast.literal_eval(NotificationType.objects.get(
                        id=notification_type_id).notification_plugin_extra_params)

        k, extra_params = get_class_name_and_extra_params(plugin_name.lower())
        output = ""

        if is_update_form:
            for field in extra_params.keys():
                field_id = extra_params[field].id
                field_value = extra_params_values[extra_params[field].id] if extra_params[
                                                                                 field].id in extra_params_values else ""
                field_label = extra_params[field].label
                field_choices = extra_params[field].choices
                output += get_component(
                        field_id,
                        field_label,
                        field_value,
                        field_choices
                )
        else:
            for field in extra_params.keys():
                output += get_component(
                        extra_params[field].id,
                        extra_params[field].label,
                        '',
                        extra_params[field].choices
                )

        res = {
            'code': 200,
            'error_id': 0,
            'html_form': output
        }

    except StandardError as e:
        raise e
        res = {
            'code': 500,
            'error': e.message,
            'html_form': "Error"
        }

    return JsonResponse(res, status=res['code'])


def get_component(_id, _label, _value='', _choices=None):
    prefix = '<div id="div_id_{0}" class="form-group has-warning">' \
           '<label for="id_{0}" class="control-label  requiredField">{1}</label>' \
           '<div class="controls ">'.format(_id, _label)

    suffix = '</div></div> '

    if _choices:
        select_control = build_select_choices(_choices, _id, _value)
        return '{0}{1}{2}'.format(prefix, select_control, suffix)
    else:
        return '{2}<input class="textinput textInput form-control" id="id_{0}"\
         maxlength="100" name="{0}" type="text" value="{1}">{3}'.format(
            _id,
            _value,
            prefix,
            suffix
            )


def build_select_choices(choices, _id, selected_value):
    prefix = '<select class="form-control input-sm" id="id_{0}" name="{0}">'.format(_id)
    suffix = '</select>'

    items = ''
    select_items = len(choices)
    items = choices[0:select_items]
    for i in items:
        val, display = i

        if val == selected_value:
            items = '{0}<option value="{1}" selected="selected">{2}</option>'.format(items,val, display)
        else:
            items = '{0}<option value="{1}">{2}</option>'.format(items,val, display)

    return "{0}{1}{2}".format(prefix, items, suffix)
