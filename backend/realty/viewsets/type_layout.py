from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from realty.models import TypeLayout
from realty.serializers import TypeLayoutSerializer


class TypeLayoutViewSet(ModelViewSet):
    serializer_class = TypeLayoutSerializer
    queryset = TypeLayout.objects.all()
    authentication_classes = (TokenAuthentication,)
