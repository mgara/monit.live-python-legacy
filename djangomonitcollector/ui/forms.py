
from django import forms
from djangomonitcollector.users.models import Settings


class SettingsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    class Meta:
        model = Settings
        fields = [
            'general_auto_add_unknown_servers',
            'general_default_timezone_for_servers',
            'flapping_threshold',
            'flapping_time_window',
            'snmp_version',
            'snmp_managers',
            'email_smtp_server',
            'email_smtp_port',
            'email_use_ssl',
            'email_sender_email',
            'email_settings_authentication',
            'email_login',
            'email_password',
        ]
