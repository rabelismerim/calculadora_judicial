from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.lawyer.models import Lawyer
from projects.abstract_project.schemas import AbstractDescriptionSchema


class LawyerSchema(AbstractDescriptionSchema):
    """Serializer Lawyer fields"""

    class Meta:
        model = Lawyer
        fields = '__all__'

    def validate(self, data):
        lawyer_name = dict(data).get('description')
        lawyer = Lawyer.objects.filter(description=lawyer_name).exists()
        if lawyer:
            raise serializers.ValidationError(['Advogado já cadastrado'])
        return super(LawyerSchema, self).validate(data)
