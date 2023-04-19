from base.schemas import AbstractDescriptionSchema
from calculation.sheets_template.models import SheetsTemplate
from rest_framework import serializers

from utils import _

class SheetsTemplateSchema(AbstractDescriptionSchema):
    """Serializer RateFile fields"""
    name = serializers.CharField()
    file = serializers.FileField()
    value = serializers.CharField()

    class Meta:
        model = SheetsTemplate
        fields = '__all__'

