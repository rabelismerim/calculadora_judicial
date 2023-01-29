from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.judge.models import Judge
from projects.abstract_project.schemas import AbstractDescriptionSchema


class JudgeSchema(AbstractDescriptionSchema):
    """Serializer Projeto fields"""

    class Meta:
        model = Judge
        fields = '__all__'


    def validate(self, data):
        judge_name = dict(data).get('description')
        judge = Judge.objects.filter(description=judge_name).exists()
        if judge:
            raise serializers.ValidationError(['Juiz já cadastrado'])
        return super(JudgeSchema, self).validate(data)
