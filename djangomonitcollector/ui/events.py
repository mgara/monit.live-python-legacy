from django_socketio.events import on_message, on_connect
from django_socketio import broadcast_channel, NoSocket, broadcast
import json
# Events
'''
on_connect(request, socket, context) - occurs once when the WebSocket connection is first established.
on_message(request, socket, context, message) - occurs every time data is sent to the WebSocket. Takes an extra message argument which contains the data sent.
on_subscribe(request, socket, context, channel) - occurs when a channel is subscribed to. Takes an extra channel argument which contains the channel subscribed to.
on_unsubscribe(request, socket, context, channel) - occurs when a channel is unsubscribed from. Takes an extra channel argument which contains the channel unsubscribed from.
on_error(request, socket, context, exception) - occurs when an error is raised. Takes an extra exception argument which contains the exception for the error.
on_disconnect(request, socket, context) - occurs once when the WebSocket disconnects.
on_finish(request, socket, context) - occurs once when the Socket.IO request is finished.
'''

# Methods
'''
django_socketio.broadcast(message)
django_socketio.broadcast_channel(message, channel)
django_socketio.send(session_id, message)
'''

@on_connect
def connect_handler(request, socket, context):
    broadcast_channel("test", "{0}".format(1))


def broadcast_to_websocket_channel(server,system):
    response = dict()
    response['cpu_user_last'] = system.cpu_user_last
    response['cpu_system_last'] = system.cpu_user_last
    response['cpu_wait_last'] = system.cpu_wait_last
    response['memory_percent_last'] = system.memory_percent_last
    response['memory_kilobyte_last'] = system.memory_kilobyte_last
    response_str = json.dumps(response)
    try:
        #broadcast(response_str)
        broadcast_channel(response_str, "{0}".format(server.id))
    except NoSocket as e:
        print e

