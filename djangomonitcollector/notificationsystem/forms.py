__author__ = 'mehergara'
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from models import NotificationType
from djangomonitcollector.datacollector.models.service import Service

#import autocomplete_light


class NotificationTypeForm(forms.ModelForm):
    notification_service = forms.ModelMultipleChoiceField(Service.objects.all(), widget=FilteredSelectMultiple("Service", False, attrs={'rows':'2'}))
    class Meta:
        model = NotificationType
        fields =[
            'notification_service',
            'notification_type',
            'notification_action',
            'notification_message',
            'notification_class'
        ]
        #autocomplete_fields = ("notification_service")

    class Media:
        js = (
            '/admin/js/core.js',
            '/admin/js/SelectBox.js',
            '/admin/js/SelectFilter2.js'
            )



