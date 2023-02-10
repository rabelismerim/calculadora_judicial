from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from projects.engagement.models import Engagement, ProjectEngagement


class EngagementSchema(AbstractModelSchema):
    """Serializer Engagement fields"""

    # project_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Engagement
        fields = ['number']


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class ProjectEngagementSchema(AbstractModelSchema):
    """Serializer ProjectEngagement fields"""

    numbers = EngagementSchema(
        many=True, source='engagement_set.all')
    # many=True, read_only=True, source='engagement_set.all')
    # numbers = EngagementSchema(many=True, write_only=True)

    user_names = serializers.ListField(read_only=True)
    users = serializers.ListField(write_only=True, child=UserSerializer())

    class Meta:
        model = ProjectEngagement
        fields = '__all__'

    def validate(self, data):
        data = dict(data)
        engagement_data = data.pop('engagements')
        list_eng = []

        if not engagement_data:
            raise serializers.ValidationError(
                ['Necessário adicionar ao menos um número de engagement'])

        if isinstance(engagement_data, list) is False:
            raise serializers.ValidationError(
                ['O campo: "engagement" deve estar no formato de lista'])

        for x in engagement_data:
            engagement_number = x.get('number')

            if Engagement.objects.filter(number=engagement_number).exists():
                raise serializers.ValidationError(
                    ['Número de engagement já cadastrado'])

            list_eng.append(engagement_number)

        data['engagements'] = list_eng
        return super(ProjectEngagementSchema, self).validate(data)
