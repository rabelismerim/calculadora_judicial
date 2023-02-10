from calculation.verdict.models import Verdict
from rest_framework import serializers
from core.abstract.models import AbstractModel


class VerdictSchema(AbstractModel):
    """Serializer Projeto fields"""

    class Meta:
        model = Verdict
        fields = '__all__'

    def validate(self, data):
        verdict_name = dict(data).get('description')
        verdict = verdict.objects.filter(description=verdict_name).exists()
        if verdict:
            raise serializers.ValidationError(['Juiz já cadastrado'])
        return super(VerdictSchema, self).validate(data)
