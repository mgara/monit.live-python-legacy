from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView, RedirectView
from models import NotificationType



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
    model = NotificationType
    fields = [
        'notification_server',
        'notification_service',
        'notification_type',
        'notification_state',
        'notification_action',
        'notification_message'
    ]


class NotificationTypeUpdate(LoginRequiredMixin, UpdateView):
    model = NotificationType
    fields = [
        'notification_server',
        'notification_service',
        'notification_type',
        'notification_state',
        'notification_action',
        'notification_message'
    ]

    def get_success_url(self):
        notification_type_id = self.kwargs['pk']
        return reverse("notifications:notificationtype_show",
                       kwargs={"pk": notification_type_id})


class NotificationTypeDelete(DeleteView):
    model = NotificationType
    success_url = reverse_lazy('notificationtype_list')

class NotificationTypeListView(LoginRequiredMixin, ListView):
    model = NotificationType

    def get_queryset(self):
        server_id = self.kwargs['pk']
        return self.model.objects.filter(server=server_id, is_ack=False).order_by('-event_time')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(EventListView, self).get_context_data(**kwargs)
        server_id = self.kwargs['pk']
        server = Server.objects.get(id=int(server_id))
        context['server'] = server
        context['alerts_count'] = server.monitevent_set.filter(is_ack=False).count()
        return context
