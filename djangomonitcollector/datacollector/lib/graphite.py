import time
import socket
import calendar


def collect_metric_from_datetime(name, value, datetime):
    timestamp = calendar.timegm(datetime.timetuple())
    collect_metric(name, value, timestamp)


def collect_metric(name, value, timestamp):

    sock = socket.socket()
    sock.connect(("localhost", 2003))
    metric = "%s %.2f %d\n" % (name, value, timestamp)
    sock.send(metric)
    sock.close()


def now():
    return int(time.time())
