from asyncore import write
from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from projects.engagement.models import Engagement, ProjectEngagement


class EngagementSchema(AbstractModelSchema):
    """Serializer Engagement fields"""

    # project_id = serializers.UUIDField()

    class Meta:
        model = Engagement
        fields = ['number']


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class ProjectEngagementSchema(AbstractModelSchema):
    """Serializer ProjectEngagement fields"""

    # numbers = EngagementSchema(
    #     many=True, source='engagement_set.all')

    numbers = serializers.ListField(source='list_engagements')
    # many=True, read_only=True, source='engagement_set.all')
    # numbers = EngagementSchema(many=True, write_only=True)

    user_names = serializers.ListField(read_only=True)
    users = serializers.ListField(write_only=True, child=UserSerializer())
    project_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ProjectEngagement
        fields = '__all__'

    def validate(self, data):
        data = dict(data)
        engagement_data = data.pop('list_engagements')
        users = data.pop('users', [])
        users = [x['id'] for x in users]
        list_eng = []

        if isinstance(engagement_data, list) is False:
            raise serializers.ValidationError(
                [f'O campo: engagement deve estar no formato de lista'])

        if not engagement_data:
            raise serializers.ValidationError(
                [f'Necessário adicionar ao menos um engagement'])

        for engagement_number in engagement_data:
            if Engagement.objects.filter(number=engagement_number).exists():
                raise serializers.ValidationError(
                    ['Número de engagement já cadastrado'])

            list_eng.append(engagement_number)

        data['engagement'] = list_eng
        data['users'] = users
        return super(ProjectEngagementSchema, self).validate(data)
