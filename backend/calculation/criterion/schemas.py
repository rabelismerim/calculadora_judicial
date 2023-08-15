from base.claim.schemas import ClaimSchema
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers
from calculation.criterion.models import Criterion


class CriterionSchema(AbstractDescriptionSchema):
    """Serializer Criterion fields"""

    calculation_id = serializers.UUIDField(write_only=True)

    claims_creditor = ClaimSchema(source='get_claims_creditor', many=True, read_only=True)
    claim_lawyer = ClaimSchema(many=False, read_only=True)

    class Meta:
        model = Criterion
        exclude = ('calculation',)
        # fields = ('calculation_id', )
        read_only_fields = ('admission', 'dismissal',
                            'default_interest', 'fine', 'advocative_hours', 'rate', 'claims_creditor', 'claim_lawyer')
    #
    # def validate_calculation_id(self, calculation_id):
    #     if Criterion.objects.filter(calculation_id=calculation_id).exists():
    #         raise serializers.ValidationError(['Critério já cadastrado'])
    #     return calculation_id
