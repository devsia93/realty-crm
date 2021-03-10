from rest_framework.serializers import ModelSerializer

from realty.models import TypePayment


class TypePaymentSerializer(ModelSerializer):
    class Meta:
        model = TypePayment
        fields = '__all__'
