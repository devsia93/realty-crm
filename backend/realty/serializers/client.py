from rest_framework.serializers import ModelSerializer

from company.serializers import WorkerSerializer
from realty.models import Client


class ClientSerializer(ModelSerializer):
    worker = WorkerSerializer

    class Meta:
        model = Client
        fields = '__all__'
