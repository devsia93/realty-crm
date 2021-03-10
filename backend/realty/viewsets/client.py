from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from realty.models import Client
from realty.serializers import ClientSerializer


class ClientViewSet(ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    authentication_classes = (TokenAuthentication,)
