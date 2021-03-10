from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from company.models import Child
from company.serializers import ChildSerializer


class ChildViewSet(ModelViewSet):
    serializer_class = ChildSerializer
    queryset = Child.objects.all()
    authentication_classes = (TokenAuthentication,)
