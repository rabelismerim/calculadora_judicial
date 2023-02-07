from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from calculation.models import Calculation
from creditors.schemas import CreditorSchema


class CalculationSchema(AbstractModelSchema):
    """Serializer Calculation fields"""

    creditor = CreditorSchema(many=False, read_only=True)
    creditor_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Calculation
        fields = '__all__'
