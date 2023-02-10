from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from base.models import AbstractDescription


class AbstractDescriptionSchema(serializers.ModelSerializer, AbstractModelSchema):
    """Serializer Projeto fields"""

    class Meta:
        model = AbstractDescription
        fields = '__all__'


class AbstractChoicesSerializer(serializers.Serializer):
    id = serializers.CharField()
    legend = serializers.CharField(max_length=1)
