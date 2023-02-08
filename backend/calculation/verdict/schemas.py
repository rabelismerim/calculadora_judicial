from calculation.verdict.models import Verdict
from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.abstract_project.schemas import AbstractDescriptionSchema


class VerdictSchema(AbstractDescriptionSchema):
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
