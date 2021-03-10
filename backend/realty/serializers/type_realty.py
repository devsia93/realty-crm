from rest_framework.serializers import ModelSerializer

from realty.models import TypeRealty


class TypeRealtySerializer(ModelSerializer):
    class Meta:
        model = TypeRealty
        fields = '__all__'
