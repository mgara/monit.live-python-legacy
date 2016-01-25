__author__ = 'mehergara'

from django import forms

from models import EVENT_STATE_CHOICES,EVENT_STATUS_CHOICES, NotificationType



class NotificationTypeForm(forms.ModelForm):
    class Meta:
        model = NotificationType
        fields =[
            'notification_service',
            'notification_service',
            'notification_type',
            'notification_action',
            'notification_message',
            'notification_class'
        ]

