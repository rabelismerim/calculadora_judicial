from rest_framework import serializers
from projects.court.models import Court
from base.schemas import AbstractDescriptionSchema
from utils import _


class CourtSchema(AbstractDescriptionSchema):
    """Serializer Court fields"""

    class Meta:
        model = Court
        fields = '__all__'

    def validate(self, data):
        court_name = dict(data).get('description')
        court = Court.objects.filter(description=court_name).exists()
        if court:
            raise serializers.ValidationError([_('Court already registered')])
        return super(CourtSchema, self).validate(data)
