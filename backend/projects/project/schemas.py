from unicodedata import name
from django.contrib.auth.password_validation import validate_password
from core.abstract.schemas import AbstractModelSchema, AbstractUpdateModelSchema
from projects.project.models import Project
from utils import get_user_model
from rest_framework import serializers


class ProjectSchema(serializers.ModelSerializer, AbstractModelSchema):
    """Serializer Projeto fields"""

    class Meta:
        model = Project
        fields = '__all__'
