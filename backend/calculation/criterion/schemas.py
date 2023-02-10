from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from calculation.criterion.models import Criterion


class CriterionSchema(AbstractModelSchema):
    """Serializer Criterion fields"""

    # judge = JudgeSchema(many=False, read_only=True)
    # judge_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Criterion
        fields = '__all__'
