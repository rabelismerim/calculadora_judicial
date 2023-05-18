from base.schemas import AbstractDescriptionSchema
from calculation.verdict.models import Verdict, TypeCalculation
from rest_framework import serializers

from utils import _


class TypeCalculationSchema(AbstractDescriptionSchema):
    """Serializer TypeCalculation fields"""

    class Meta:
        model = TypeCalculation
        fields = '__all__'


class VerdictSchema(AbstractDescriptionSchema):
    """Serializer Projeto fields"""

    type_calculation = TypeCalculationSchema(many=False, read_only=False)
    calculation_id = serializers.UUIDField()

    class Meta:
        model = Verdict
        exclude = ('calculation',)

    def validate(self, data):
        verdict_name = data.get('description')
        calculation_id = dict(data).get('calculation_id')
        verdict = Verdict.objects.filter(
            description=verdict_name, calculation_id=calculation_id).exists()
        if verdict:
            raise serializers.ValidationError([_('Verdict already registered')])
        return super(VerdictSchema, self).validate(data)
