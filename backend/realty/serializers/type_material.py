from rest_framework.serializers import ModelSerializer

from realty.models import TypeMaterial


class TypeMaterialSerializer(ModelSerializer):
    class Meta:
        model = TypeMaterial
        fields = '__all__'
