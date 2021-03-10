from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication

from company.models import Task
from company.serializers import TaskSerializer


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    authentication_classes = (TokenAuthentication,)
