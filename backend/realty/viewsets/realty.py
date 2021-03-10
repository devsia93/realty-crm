from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from realty.models import Realty
from realty.serializers import RealtySerializer


class RealtyViewSet(ModelViewSet):
    serializer_class = RealtySerializer
    queryset = Realty.objects.all()
    authentication_classes = (TokenAuthentication,)
