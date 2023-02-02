from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.project_user.models import ProjectUser
from projects.abstract_project.schemas import AbstractDescriptionSchema


class ProjectUserSchema(AbstractDescriptionSchema):
    """Serializer ProjectUser fields"""

    class Meta:
        model = ProjectUser
        fields = '__all__'
