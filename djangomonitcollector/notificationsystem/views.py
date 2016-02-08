from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from models import NotificationType, Notification
from forms import NotificationTypeForm, get_class_name_and_extra_params
from django import forms
from django.http import JsonResponse

def notificationtypeactivation(request):
    pass

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

    def get_context_data(self, **kwargs):
        context = super(NotificationTypeCreate, self).get_context_data(**kwargs)
        context['form'].fields['notification_user'] = forms.CharField(widget=forms.HiddenInput(),
                                                                      initial=self.request.user.id
                                                                      )
        return context


class NotificationTypeUpdate(LoginRequiredMixin, UpdateView):
    model = NotificationType
    fields = [
        'notification_service',
        'notification_type',
        'notification_state',
        'notification_action',
        'notification_message'
    ]

    def get_success_url(self):
        notification_type_id = self.kwargs['pk']
        return reverse_lazy("n:notificationtype_show",
                            kwargs={"pk": notification_type_id})

class NotificationTypeDelete(DeleteView):
    model = NotificationType
    success_url = reverse_lazy('n:notificationtype_list')


class NotificationTypeListView(LoginRequiredMixin, ListView):
    model = NotificationType

    def get_queryset(self):
        user = self.request.user
        return self.model.objects.filter(notification_user=user)


class NotificationView(LoginRequiredMixin, DetailView):
    model = Notification

    fields = [
        'notification_type',
        'notification_event',
    ]

    def get_object(self):
        notification_type_id = self.kwargs['pk']
        # Only get the User record for the user making the request
        return Notification.objects.get(id=notification_type_id)


class NotificationDelete(LoginRequiredMixin, DeleteView):
    model = NotificationType
    success_url = reverse_lazy('n:notification_list')


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification

    def get_queryset(self):
        user = self.request.user
        return self.model.objects.filter(notification_user=user)


def get_notification_plugin_form(request):
    try:
        plugin_name = request.GET['plugin_name']
        k,extra_params = get_class_name_and_extra_params(plugin_name.lower())
        output = ""
        for field in extra_params.keys():
            output+=get_component(extra_params[field].id,extra_params[field].label)

        res = {
            'error_id' : 0,
            'html_form' : output
        }

    except StandardError as e:
        res = {
            'error': e.message,
            'html_form': "Error"
        }

    return JsonResponse(res)

def get_component(_id,_label):
    return '<div id="div_id_{0}" class="form-group has-warning">' \
           '<label for="id_{0}" class="control-label  requiredField">{1}</label>' \
           '<div class="controls ">' \
           '<input class="textinput textInput form-control" id="id_{0}" maxlength="100" name="{0}" type="text"> </div>' \
           '</div> '.format(_id,_label)
