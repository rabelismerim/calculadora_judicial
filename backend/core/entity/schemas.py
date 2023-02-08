from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers

from core.entity.models import Entity


class EntitySchema(AbstractModelSchema):
    """Serializer Entity fields"""

    class Meta:
        model = Entity
        fields = '__all__'
