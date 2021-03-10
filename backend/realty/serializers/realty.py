from rest_framework.serializers import ModelSerializer

from realty.models import Realty


class RealtySerializer(ModelSerializer):
    class Meta:
        model = Realty
        fields = '__all__'
