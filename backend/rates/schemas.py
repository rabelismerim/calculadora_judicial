from numpy import source
from base.schemas import AbstractDescriptionSchema
from rates.models import Rate
from rest_framework import serializers


class RateSchema(AbstractDescriptionSchema):
    """Serializer Rate fields"""

    index_display = serializers.CharField(
        source='get_index_display', read_only=True)

    class Meta:
        model = Rate
        fields = '__all__'
