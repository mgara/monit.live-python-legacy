from djangomonitcollector.users.models import APIKey
from rest_framework import authentication
from rest_framework import exceptions

class KairosTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_X_API_TOKEN')

        if not token:
            raise exceptions.AuthenticationFailed('No token Provided')


        try:
            api_key = APIKey.objects.get(api_key=token)
        except ValueError:
             raise exceptions.AuthenticationFailed('Bad API Token')
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such token')

        return (api_key.organisation, None)
