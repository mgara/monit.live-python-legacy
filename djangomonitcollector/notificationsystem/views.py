import ast
import re
import os

from braces.views import LoginRequiredMixin
from django import forms
from django.core import serializers
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template import defaultfilters
from django.template.loader import render_to_string
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from djangomonitcollector.datacollector.models import Server, MonitEvent, MonitEventComment
from forms import NotificationTypeForm, get_class_name_and_extra_params
from models import NotificationType


def check_item(item, string_list_of_items):
    if not string_list_of_items.strip():
        return True
    try:
        list_of_items = ast.literal_eval(string_list_of_items)
    except StandardError as e:
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


def clean_file_name_and_filesystem_name(filesystem_raw_service_name):
    if filesystem_raw_service_name.startswith("___") or\
            filesystem_raw_service_name.startswith("__") or\
            filesystem_raw_service_name.startswith("_"):
        filesystem_raw_service_name = filesystem_raw_service_name.\
            replace("___", '/').replace("__", '/').replace("_", '/')
    return filesystem_raw_service_name.replace("//", '/')


def get_user_services(org):
    '''
    This function returns the list of the services assigned to the current organisation
    '''
    user_servers = Server.objects.filter(organisation=org)
    service_list = tuple()

    items = list()

    for server in user_servers:
        items += server.process_set.all().order_by('name')
        items += server.program_set.all().order_by('name')
        items += server.file_set.all().order_by('name')
        items += server.net_set.all().order_by('name')
        items += server.directory_set.all().order_by('name')
        items += server.filesystem_set.all().order_by('name')
        items += server.host_set.all().order_by('name')
        items.append(server.system)

    items = (i.name for i in items)  # get the name only
    items = list(set(items))  # remove duplicates
    items = sorted(items)
    service_list += tuple((i, clean_file_name_and_filesystem_name(i))
                          for i in items)  # create final tuple
    return service_list


class NotificationTypeView(LoginRequiredMixin, DetailView):
    model = NotificationType
    fields = [
        'notification_host_group',
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

    def get_context_data(self, **kwargs):
            notification_type_id = self.kwargs['pk']

            # Call the base implementation first to get a context
            context = super(NotificationTypeView, self).get_context_data(**kwargs)
            # Add in a QuerySet of all the books

            self.err_log = "{}/plugin_error_output/{}_err_log".format(os.getcwd(), notification_type_id)
            self.std_log = "{}/plugin_std_output/{}_std.log".format(os.getcwd(), notification_type_id)

            std = self.get_file_content(self.std_log)
            err = self.get_file_content(self.err_log)

            context['std_log'] = '\n'.join(map(str, std))
            context['err_log'] = '\n'.join(map(str, err))

            return context

    def get_file_content(self,file_name):
        res = []
        #res.append(file_name)
        dir_name = os.path.dirname(file_name)
        #res.append(dir_name)
        if not os.path.exists(dir_name):
            res.append("Directory Not Found, Please contact help")
            return res
        if not os.path.exists(file_name):
            res.append("File Not Found, This error may occur if this rule has never been applied before.")
            return res

        try:
            from sh import tail
            # return last 10 lines
            for line in tail("-n100",file_name, _iter=True):
                if len(line.strip())>0:
                    res.append(line.replace("\n","").rstrip())
            return res
        except Exception as e:
            l = "A problem accured when trying to read the file"
            res.append(l)
            res.append("{}".format(e))
            return res

class NotificationTypeCreate(LoginRequiredMixin, CreateView):
    form_class = NotificationTypeForm
    model = NotificationType

    def form_invalid(self, form):
        return super(NotificationTypeCreate, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.organisation = self.request.user.organisation
        form.instance.notification_user = self.request.user
        return super(NotificationTypeCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(
            NotificationTypeCreate, self).get_context_data(**kwargs)
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

    def get_queryset(self):
        org = self.request.user.organisation

        return self.model.objects.filter(organisation=org)


#  Ajax Request (protected by csrf token)
def get_notification_plugin_form(request):
    try:
        is_update_form = 'notification_type_id' in request.GET
        plugin_name = request.GET['plugin_name']
        if is_update_form:
            notification_type_id = request.GET['notification_type_id']
            if notification_type_id.strip():
                extra_params_values = ast.literal_eval(NotificationType.objects.get(
                    id=notification_type_id).notification_plugin_extra_params)

        k, extra_params, klass = get_class_name_and_extra_params(
            plugin_name.lower())
        output = ""

        if is_update_form:
            for field in extra_params.keys():
                field_id = extra_params[field].id
                field_value = extra_params_values[extra_params[field].id] if extra_params[
                    field].id in extra_params_values else ""
                field_label = extra_params[field].label
                field_choices = extra_params[field].choices
                field_help_block = extra_params[field].help_block
                output += get_component(
                    field_id,
                    field_label,
                    field_value,
                    field_choices,
                    field_help_block
                )
        else:
            for field in extra_params.keys():
                output += get_component(
                    extra_params[field].id,
                    extra_params[field].label,
                    '',
                    extra_params[field].choices,
                    extra_params[field].help_block
                )
            plugin_help_message = klass().get_helpmessage()

        res = {
            'code': 200,
            'error_id': 0,
            'html_form': output,
            'help_message': plugin_help_message
        }

    except StandardError as e:
        raise e
        res = {
            'code': 500,
            'error': e.message,
            'html_form': "Error"
        }

    return JsonResponse(res, status=res['code'])


def get_component(_id, _label, _value='', _choices=None, _help_block=None):
    fg_line = "fg-line"
    if _choices:
        fg_line = ""
    prefix = '<div id="div_id_{0}" class="form-group">' \
        '<label for="id_{0}" class="control-label  requiredField">{1}</label>' \
        '<div class="controls {2}">'.format(_id, _label, fg_line)
    if _help_block:
        help_block = '<span class="help-block m-b-none">{}</span>'.format(
            _help_block)
        suffix = '</div>{}</div> '.format(help_block)
    else:
        suffix = '</div></div>'

    if _choices:
        select_control = build_select_choices(_choices, _id, _value)
        comp = '{0}{1}{2}'.format(prefix, select_control, suffix)
    else:
        comp = '{2}<input class="textinput textInput form-control" id="id_{0}"\
         maxlength="100" name="{0}" type="text" value="{1}">{3}'.format(
            _id,
            _value,
            prefix,
            suffix
        )

    return comp


def build_select_choices(choices, _id, selected_value):
    prefix = '<select class="form-control col-md-3" id="id_{0}" name="{0}">'.format(
        _id)
    suffix = '</select>'

    items = ''
    select_items = len(choices)
    items = choices[0:select_items]
    for i in items:
        val, display = i

        if val == selected_value:
            items = '{0}<option value="{1}" selected="selected">{2}</option>'.format(
                items, val, display)
        else:
            items = '{0}<option value="{1}">{2}</option>'.format(
                items, val, display)

    return "{0}{1}{2}".format(prefix, items, suffix)


#  Ajax Request (protected by csrf token)
def get_event_details(request):
    event_id = request.POST['event_id']
    activate_comment_window = request.POST['comments_window']
    comments = False
    if activate_comment_window == "true":
        comments = True
    event_id = int(event_id)
    monit_event = MonitEvent.objects.get(pk=event_id)

    html = render_to_string(
        'ui/includes/_event_details.html', {'monit_event': monit_event, 'current_user': request.user, 'comments': comments})
    return JsonResponse(html, safe=False)


#  Ajax Request (protected by csrf token)
def get_event_row(request):
    event_id = request.POST['event_id']
    event_id = int(event_id)
    monit_event = MonitEvent.objects.get(pk=event_id)

    table_html = render_to_string(
        'ui/includes/_event_row.html', {'monit_event': monit_event})
    return JsonResponse({'row': table_html})


def remove_unicode_u(unicode_string):
    no_unicode = unicode_string.replace("u\'", "'").replace("u\"", '"')
    convert_single_quotes = no_unicode.replace('\'', '"')
    return convert_single_quotes


#  Ajax Request (protected by csrf token)
def get_notification_details(request):
    notification_id = request.POST['notification_id']
    notification = NotificationType.objects.get(pk=notification_id)

    #  I had to do this because I need the string to
    #  be clean on the javascript side as I'm parsing the array to JSON.
    if notification.notification_type:
        notification.notification_type = remove_unicode_u(
            notification.notification_type)
    if notification.notification_service:
        notification.notification_service = remove_unicode_u(
            notification.notification_service)
    if notification.notification_action:
        notification.notification_action = remove_unicode_u(
            notification.notification_action)
    if notification.notification_state:
        notification.notification_state = remove_unicode_u(
            notification.notification_state)

    data = serializers.serialize("json", [notification, ])
    return JsonResponse(data, safe=False)


#  Ajax Request (protected by csrf token)
def postcomment(request):
    res = dict()
    try:

        event_id = request.POST['event_id']
        comment = request.POST['comment']
        comment = comment.lstrip().rstrip()
        action = request.POST['action']
        comment_id = request.POST['comment_id']
        event_id = int(event_id)
        monit_event = MonitEvent.objects.get(pk=event_id)

        if action == "new":

            current_user = request.user
            comment_obj = MonitEventComment.create(
                current_user,
                monit_event,
                comment
            )
        elif action == "update":
            comment_obj = MonitEventComment.objects.get(pk=int(comment_id))
            comment_obj.content = comment
            comment_obj.save()
        else:
            comment_obj = MonitEventComment.objects.get(pk=int(comment_id))
            comment_obj.delete()

        comments_count = MonitEventComment.objects.filter(
            event=monit_event).count()
        res = {
            'code': 200,
            'error_id': 0,
            'count': comments_count,
            'html': get_comment_html(comment_obj, request.user)
        }

    except StandardError as e:
        raise e
        res = {
            'code': 500,
            'error_id': e.message,
        }

    return JsonResponse(res, status=res['code'])


def get_comment_html(comment, user):
    toolbox = ""
    if user == comment.user:
        toolbox = "<div  role=\"group\" aria-label=\"First group\"> \
        <button class=\"btn btn-circle btn-danger pull-right btn-delete\" onclick=\"alert('dd')\" comment-id=\"{0}\"><i class=\"fa fa-trash\"></i></button>\
                <button type=\"button\" class=\"btn btn-circle btn-primary pull-right btn-edit\" comment-id=\"{0}\"><i class=\"fa fa-edit\"></i></button>\
            </div>".format(comment.id)

    #  Disabled for now cause the button are not working
    #toolbox =""
    return " <div class=\"row clearfix list-group-item\" id=\"comment-{0}\">\
                            <div class=\"col-md-12 list-group-item-text\">\
                             <b>{1}</b> added a comment -  {2}\
                             <p class=\"text-info\">\
                             {3}\
                             </p>\
                             {4}\
                            </div>\
                        </div>".format(
        comment.id,
        defaultfilters.title(comment.user),
        defaultfilters.date(comment.created_at),
        comment.content,
        toolbox
    )
