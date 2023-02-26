from rest_framework import serializers
from projects.court.models import Court
from base.schemas import AbstractDescriptionSchema


class CourtSchema(AbstractDescriptionSchema):
    """Serializer Court fields"""

    class Meta:
        model = Court
        fields = '__all__'

    def validate(self, data):
        court_name = dict(data).get('description')
        court = Court.objects.filter(description=court_name).exists()
        if court:
            raise serializers.ValidationError(['Vara já cadastrada'])
        return super(CourtSchema, self).validate(data)
