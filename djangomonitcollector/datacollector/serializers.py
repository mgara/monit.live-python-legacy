

from rest_framework import serializers
from djangomonitcollector.datacollector.models import Server, MonitEvent


class ServerSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Server
        fields = (
            'id',
            'address',
            'data_timezone',
            'external_ip',
            'http_address',
            'http_password',
            'http_username',
            'disable_monitoring',
            'localhostname',
            'monit_id',
            'monit_update_period',
            'monit_version',
            'server_up',
            'uptime',
            'last_data_received',
        )

    def update(self, instance, validated_data):
        """
        Update and return an existing `Server` instance, given the validated data.
        """
        instance.disable_monitoring = validated_data.get(
            'disable_monitoring', instance.disable_monitoring)
        instance.save()
        return instance


class AlertSerializer(serializers.HyperlinkedModelSerializer):
    server = serializers.ReadOnlyField(source='server.localhostname')

    class Meta:
        model = MonitEvent
        fields = (
            'id',
            'server',
            'event_message',
            'event_time',
            'updated_at',
            'created_at',
            'is_ack',
            'cleared_alarms',
            'is_active',
            'cleared_by',
            'is_duplicate_of',
            'alarm_raised',
        )
