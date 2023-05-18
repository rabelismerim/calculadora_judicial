from rest_framework import serializers
from projects.lawyer.models import Lawyer
from base.schemas import AbstractDescriptionSchema
from utils import _


class LawyerSchema(AbstractDescriptionSchema):
    """Serializer Lawyer fields"""

    class Meta:
        model = Lawyer
        fields = '__all__'

    def validate(self, data):
        lawyer_name = dict(data).get('description')
        lawyer = Lawyer.objects.filter(description=lawyer_name).exists()
        if lawyer:
            raise serializers.ValidationError([_('Lawyer already registered')])
        return super(LawyerSchema, self).validate(data)
