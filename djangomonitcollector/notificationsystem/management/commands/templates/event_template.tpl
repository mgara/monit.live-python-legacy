<?xml version="1.0" encoding="ISO-8859-1"?>
<monit id="${monit_instance_id}" incarnation="1455554286" version="5.15" externalevent="True">
    <server>
        <localhostname>${localhostname}</localhostname>
    </server>
    <event>
        <collected_sec>${collected_sec}</collected_sec>
        <collected_usec>${collected_usec}</collected_usec>
        <service>${localhostname}</service>
        <type>${event_type}</type>
        <id>${event_id}</id>
        <state>${event_state}</state>
        <action>${event_action}</action>
        <message><![CDATA[${event_message}]]></message>
    </event>
</monit>
