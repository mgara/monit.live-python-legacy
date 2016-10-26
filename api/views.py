
# Create your views here.

from auth import KairosTokenAuthentication
from django.http import Http404
from djangomonitcollector.datacollector.models import Server, MonitEvent
from djangomonitcollector.datacollector.serializers import ServerSerializer, AlertSerializer
from djangomonitcollector.users.models import User
from djangomonitcollector.users.serializers import UserSerializer
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from coreapi import Link


class ServerDetail(APIView):
    authentication_classes = (
        SessionAuthentication, BasicAuthentication, KairosTokenAuthentication)
    permission_classes = (IsAuthenticated,)

    """
    Retrieve, update or delete a server instance.
    """

    def get_object(self, pk):
        try:
            return Server.objects.get(id=pk)
        except Server.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        server = self.get_object(pk)
        serializer = ServerSerializer(server)
        return Response(serializer.data)

    """
    Update a server instance.
    """

    def put(self, request, pk, format=None):
        server = self.get_object(pk)
        serializer = ServerSerializer(server, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        server = self.get_object(pk)
        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AlertDetail(APIView):
    authentication_classes = (
        SessionAuthentication, BasicAuthentication, KairosTokenAuthentication)
    permission_classes = (IsAuthenticated,)

    """
    get: Create a new user.
    post: List all the users.
    """

    def get_object(self, pk):
        try:
            return MonitEvent.objects.get(id=pk)
        except MonitEvent.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        alert = self.get_object(pk)
        serializer = AlertSerializer(alert, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        alert = self.get_object(pk)
        serializer = AlertSerializer(alert)
        return Response(serializer.data)


class ServerAlertList(APIView):

    """
    List all servers, or create a new server.
    """

    def get(self, request, pk, format=None):
        server = Server.objects.get(id=pk)
        alerts = MonitEvent.objects.filter(server=server)
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)


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
