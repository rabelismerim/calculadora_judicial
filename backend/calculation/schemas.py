from calculation.criterion.schemas import CriterionSchema
from calculation.funds.schemas import FundsSchema
from calculation.verdict.schemas import VerdictSchema
from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from calculation.models import Calculation
from creditors.schemas import CreditorSchema


class CalculationSchema(AbstractModelSchema):
    """Serializer Calculation fields"""

    creditor = CreditorSchema(many=False, read_only=True)
    creditor_id = serializers.UUIDField(write_only=True)
    verdict = VerdictSchema(source='verdict_set',
                            many=True, required=False, exclude=('calculation_id', ))
    criterion = CriterionSchema(many=False, read_only=True)

    funds = FundsSchema(source='funds_set', many=True,
                        required=False, exclude=('calculation_id', ))

    class Meta:
        model = Calculation
        fields = '__all__'

    def validate(self, data):
        data['verdict'] = data.pop('verdict_set', None)
        data['funds'] = data.pop('funds_set', None)
        return super(CalculationSchema, self).validate(data)
