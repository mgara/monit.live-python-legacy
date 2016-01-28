from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from models import NotificationType
from models import Notification, EVENT_STATUS_CHOICES,EVENT_STATE_CHOICES ,EVENT_ACTION_CHOICES
from djangomonitcollector.datacollector.models.service import Service
from forms import NotificationTypeForm
from django import forms




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
        # Only get the User record for the user making the request
        return User.objects.get(id=notification_type_id)


class NotificationTypeCreate(LoginRequiredMixin, CreateView):
    form_class = NotificationTypeForm
    model = NotificationType
    def get_context_data(self, **kwargs):
        context = super(NotificationTypeCreate, self).get_context_data(**kwargs)
        for service in  Service.objects.all():
        	if service.service_type==8:
        		print service.net.server
        context['form'].fields['notification_type'] = forms.MultipleChoiceField(choices=EVENT_STATUS_CHOICES)
        context['form'].fields['notification_state'] = forms.MultipleChoiceField(choices=EVENT_STATE_CHOICES)
        context['form'].fields['notification_action'] = forms.MultipleChoiceField(choices=EVENT_ACTION_CHOICES)
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
    success_url = reverse_lazy('notificationtype_list')


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


class NotificationDelete(DeleteView):
    model = NotificationType
    success_url = reverse_lazy('notification_list')


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification

    def get_queryset(self):
        user = self.request.user
        return self.model.objects.filter(notification_user=user)
