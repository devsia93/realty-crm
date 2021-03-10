from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from realty.models import TypeMaterial
from realty.serializers import TypeMaterialSerializer


class TypeMaterialViewSet(ModelViewSet):
    serializer_class = TypeMaterialSerializer
    queryset = TypeMaterial.objects.all()
    authentication_classes = (TokenAuthentication,)
