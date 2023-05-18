from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from projects.engagement.models import Engagement, ProjectEngagement
from utils import _


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
    project_id = serializers.UUIDField()

    class Meta:
        model = ProjectEngagement
        fields = '__all__'

    def validate(self, data):
        data = dict(data)
        engagement_data = data.pop('list_engagements')
        users = data.pop('users', [])
        users = [x['id'] for x in users]
        list_eng = []
        list_eng_error = []

        if isinstance(engagement_data, list) is False:
            raise serializers.ValidationError([_('The field engagement must be in list format')])

        if not engagement_data:
            raise serializers.ValidationError([_('Need to add at least one engagement')])

        list_engagements_number = list(Engagement.objects.filter(
            number__in=engagement_data).values_list('number', flat=True))
        for engagement_number in engagement_data:
            if engagement_number in list_engagements_number:
                list_eng_error.append(_('Engagement number {} is already registered').format(engagement_number))
            else:
                list_eng.append(engagement_number)

        if list_eng_error:
            raise serializers.ValidationError(list_eng_error)

        data['engagement'] = list_eng
        data['users'] = users
        return super(ProjectEngagementSchema, self).validate(data)
