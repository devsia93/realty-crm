from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from realty.models import Deal
from realty.serializers import DealSerializer


class DealViewSet(ModelViewSet):
    serializer_class = DealSerializer
    queryset = Deal.objects.all()
    authentication_classes = (TokenAuthentication,)
