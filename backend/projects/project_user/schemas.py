from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from projects.project_user.models import ProjectUser


class ProjectUserSchema(AbstractModelSchema):
    """Serializer ProjectUser fields"""
    user = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProjectUser
        fields = '__all__'

        read_only_fields = ('groups', 'permissions', 'id')
