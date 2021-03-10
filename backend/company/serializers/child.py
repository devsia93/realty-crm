from rest_framework.serializers import ModelSerializer

from company.models import Child


class ChildSerializer(ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'
