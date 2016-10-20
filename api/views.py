
# Create your views here.

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from djangomonitcollector.datacollector.models import Server
from djangomonitcollector.datacollector.serializers import ServerSerializer
from rest_framework import viewsets
from djangomonitcollector.users.models import User
from djangomonitcollector.users.serializers import UserSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from auth import KairosTokenAuthentication

class ServerDetail(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication, KairosTokenAuthentication)
    permission_classes = (IsAuthenticated,)

    """
    Retrieve, update or delete a server instance.
    """
    def get_object(self, id):
        try:
            return Server.objects.get(id=id)
        except Server.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        server = self.get_object(id)
        serializer = ServerSerializer(server)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        server = self.get_object(id)
        serializer = ServerSerializer(server, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        server = self.get_object(id)
        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OnlineServerList(APIView):
    """
    List all servers, or create a new server.
    """
    def get(self, request, format=None):
        servers = Server.objects.filter(server_up=True)
        serializer = ServerSerializer(servers, many=True)
        return Response(serializer.data)

class OfflineServerList(APIView):
    """
    List all servers, or create a new server.
    """
    def get(self, request, format=None):
        servers = Server.objects.filter(server_up=False)
        serializer = ServerSerializer(servers, many=True)
        return Response(serializer.data)

class ServerList(APIView):
    authentication_classes = (KairosTokenAuthentication,)

    """
    List all servers, or create a new server.
    """
    def get(self, request, format=None):
        servers = Server.objects.all()
        serializer = ServerSerializer(servers, many=True)
        return Response(serializer.data)


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
