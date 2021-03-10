from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from realty.models import TypePayment
from realty.serializers import TypePaymentSerializer


class TypePaymentViewSet(ModelViewSet):
    serializer_class = TypePaymentSerializer
    queryset = TypePayment.objects.all()
    authentication_classes = (TokenAuthentication,)

