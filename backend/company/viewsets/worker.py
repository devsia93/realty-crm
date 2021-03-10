from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from company.models import Worker
from company.serializers import WorkerSerializer


class WorkerViewSet(ModelViewSet):
    serializer_class = WorkerSerializer
    queryset = Worker.objects.all()
    authentication_classes = (TokenAuthentication,)
