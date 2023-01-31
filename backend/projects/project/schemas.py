from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.judge.schemas import JudgeSchema
from projects.layer.schemas import LayerSchema
from projects.region.schemas import RegionSchema
from projects.engagement.schemas import ProjectEngagementSchema


class ProjectSchema(serializers.ModelSerializer, AbstractModelSchema):
    """Serializer Projeto fields"""

    judge = JudgeSchema(many=False, read_only=True)
    judge_id = serializers.UUIDField(write_only=True)

    layer = LayerSchema(many=False, read_only=True)
    layer_id = serializers.UUIDField(write_only=True)

    region = RegionSchema(many=False, read_only=True)
    region_id = serializers.UUIDField(write_only=True)
    
    engagement = ProjectEngagementSchema(many=False)


    class Meta:
        model = Project
        fields = '__all__'
