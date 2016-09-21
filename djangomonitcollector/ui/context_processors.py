from djangomonitcollector.datacollector.models import MonitEvent

from django.conf import settings # import the settings file


def app_settings(request):

    # return the value you want as a dictionnary. you may add multiple values in there.
    user = request.user
    organisation_events = None

    if user.is_authenticated():
        org = user.organisation
        organisation_events = MonitEvent.objects.filter(server__organisation=org).order_by('-id')[:10]

    return {
        'APPNAME': settings.APPNAME,
        'APPVERSION': settings.APPVERSION,
        'APIVERSION': settings.APIVERSION,
        'organisation_events': organisation_events
    }
