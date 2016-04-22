import pytz

from django.utils import timezone
from datetime import datetime, timedelta


class TimezoneMiddleware(object):
    def process_request(self, request):
        try:
            tzname = request.user.user_timezone
            if tzname:
                tz = pytz.timezone(tzname)
                timezone.activate(tz)
                request.session['is_dst'] = is_dst(tzname)
        except:
            timezone.deactivate()


def is_dst(zonename):
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)
