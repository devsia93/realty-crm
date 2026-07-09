from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.serializers import ModelSerializer

from realty import services
from realty.models import Deal


class DealSerializer(ModelSerializer):
    """Deal API write path routes through realty.services so the main_worker
    auto-assignment (and the owner-chain ValidationError) has a single home.

    DRF (3.12) only auto-converts django.core.exceptions.ValidationError during
    serializer.is_valid(); create()/update() are NOT wrapped, so the service's
    Django ValidationError is converted here to a DRF ValidationError -> HTTP
    400. Bogus-FK 400s are unaffected: they fail in is_valid()
    (PrimaryKeyRelatedField rejects unknown PKs) before the service ever runs.
    """

    class Meta:
        model = Deal
        fields = '__all__'

    def create(self, validated_data):
        try:
            return services.create_deal(**validated_data)
        except DjangoValidationError as exc:
            raise DRFValidationError(detail=exc.messages)

    def update(self, instance, validated_data):
        try:
            return services.update_deal(instance, **validated_data)
        except DjangoValidationError as exc:
            raise DRFValidationError(detail=exc.messages)
