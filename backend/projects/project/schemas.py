from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.judge.schemas import JudgeSchema
from projects.lawyer.schemas import LawyerSchema
from projects.region.schemas import RegionSchema
from projects.engagement.schemas import EngagementSchema, ProjectEngagementSchema


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class ProjectSchema(serializers.ModelSerializer, AbstractModelSchema):
    """Serializer Project fields"""

    judge = JudgeSchema(many=False, read_only=True)
    judge_id = serializers.UUIDField(write_only=True)

    lawyer = LawyerSchema(many=False, read_only=True)
    lawyer_id = serializers.UUIDField(write_only=True)

    region = RegionSchema(many=False, read_only=True)
    region_id = serializers.UUIDField(write_only=True)

    # engagement = ProjectEngagementSchema(many=False)

    engagement = EngagementSchema(many=True, write_only=True)

    user_names = serializers.ListField(read_only=True)
    users = serializers.ListField(write_only=True, child=UserSerializer())

    status_display = serializers.CharField(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
