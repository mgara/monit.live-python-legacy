import time
import socket
import calendar

import errno
from socket import error as socket_error


def collect_metric_from_datetime(name, value, datetime):
    timestamp = calendar.timegm(datetime.timetuple())
    collect_metric(name, value, timestamp)


def collect_metric(name, value, timestamp):
    metric = "%s %.2f %d\n" % (name, value, timestamp)

    try:
        sock = socket.socket()
        sock.connect(("localhost", 2003))
        sock.send(metric)
    except socket_error as serr:
        if serr.errno != errno.ECONNREFUSED:
            # Not the error we are looking for, re-raise
            raise serr
        print "Queued : {}".format(metric)
    sock.close()


def now():
    return int(time.time())
