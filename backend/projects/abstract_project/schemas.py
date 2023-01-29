from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.abstract_project.models import AbstractDescription, AbstractInfo


class AbstractDescriptionSchema(serializers.ModelSerializer, AbstractModelSchema):
    """Serializer Projeto fields"""

    class Meta:
        model = AbstractDescription
        fields = '__all__'
