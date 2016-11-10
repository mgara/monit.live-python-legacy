from djangomonitcollector.users.models import APIKey
from rest_framework import authentication
from rest_framework import exceptions


class KairosTokenAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        # X-API-TOKEN
        token = request.META.get('HTTP_X_API_TOKEN')

        if not token:
            raise exceptions.AuthenticationFailed(
                'No token Provided, The X-API-TOKEN request header is required \
in order to use the API. Please include the following header \
with all requests: X-API-TOKEN: {your-api-key}')

        try:
            api_key = APIKey.objects.get(api_key=token)
        except ValueError:
            raise exceptions.AuthenticationFailed('Bad API Token')
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such token')

        return (api_key.organisation, None)
