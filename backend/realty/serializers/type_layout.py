from rest_framework.serializers import ModelSerializer

from realty.models import TypeLayout


class TypeLayoutSerializer(ModelSerializer):
    class Meta:
        model = TypeLayout
        fields = '__all__'
