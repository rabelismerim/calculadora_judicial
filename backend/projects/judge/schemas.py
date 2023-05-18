from rest_framework import serializers
from projects.judge.models import Judge
from base.schemas import AbstractDescriptionSchema
from utils import _


class JudgeSchema(AbstractDescriptionSchema):
    """Serializer Projeto fields"""

    class Meta:
        model = Judge
        fields = '__all__'

    def validate(self, data):
        judge_name = dict(data).get('description')
        judge = Judge.objects.filter(description=judge_name).exists()
        if judge:
            raise serializers.ValidationError([_('Judge already registered')])
        return super(JudgeSchema, self).validate(data)
