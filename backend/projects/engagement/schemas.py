from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.engagement.models import Engagement, ProjectEngagement
from projects.abstract_project.schemas import AbstractDescriptionSchema
from projects.project_user.schemas import ProjectUserSchema


class EngagementSchema(AbstractDescriptionSchema):
    """Serializer Engagement fields"""

    # project_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Engagement
        fields = ['number']


class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class ProjectEngagementSchema(AbstractDescriptionSchema):
    """Serializer ProjectEngagement fields"""

    numbers = EngagementSchema(
        many=True, read_only=True, source='engagement_set.all')
    numbers = EngagementSchema(many=True, write_only=True)

    user_names = serializers.ListField(read_only=True)
    users = serializers.ListField(write_only=True, child=UserSerializer())

    class Meta:
        model = ProjectEngagement
        fields = '__all__'

    def validate(self, data):
        data = dict(data)
        engagement_data = data.pop('engagement')
        print(engagement_data, 'engagement_data\n\n')
        list_eng = []
        for x in engagement_data:
            engagement_number = x.get('number')

            if Engagement.objects.filter(number=engagement_number).exists():
                raise serializers.ValidationError(
                    ['Número de engagement já cadastrado'])

            list_eng.append(engagement_number)

        data['engagement'] = {'numbers':  list_eng}
        return super(ProjectEngagementSchema, self).validate(data)
