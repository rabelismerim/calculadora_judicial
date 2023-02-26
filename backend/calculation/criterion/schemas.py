from base.claim.schemas import ClaimSchema
from base.schemas import AbstractDescriptionSchema
from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from calculation.criterion.models import Criterion


class CriterionSchema(AbstractDescriptionSchema):
    """Serializer Criterion fields"""

    calculation_id = serializers.UUIDField(write_only=True)

    claim_credor = ClaimSchema(many=False, read_only=True)
    claim_lawyer = ClaimSchema(many=False, read_only=True)

    class Meta:
        model = Criterion
        exclude = ('calculation', )
        # fields = ('calculation_id', )
        read_only_fields = ('admission', 'dismissal',
                            'default_interest', 'fine', 'advocative_hours', 'rate', 'claim_credor', 'claim_lawyer')

    def validate_calculation_id(self, calculation_id):
        if Criterion.objects.filter(calculation_id=calculation_id).exists():
            raise serializers.ValidationError(['Critério já cadastrado'])
        return calculation_id
