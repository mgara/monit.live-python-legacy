import time
import socket
import calendar


def collect_metric_from_datetime(name, value, datetime):
    timestamp = calendar.timegm(datetime.timetuple())
    collect_metric(name, value, timestamp)


def collect_metric(name, value, timestamp):

    sock = socket.socket()
    sock.connect(("localhost", 2003))
    sock.send("%s %d %d\n" % (name, value, timestamp))
    sock.close()


def now():
    return int(time.time())
