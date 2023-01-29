from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.region.models import Region
from projects.abstract_project.schemas import AbstractDescriptionSchema


class RegionSchema(AbstractDescriptionSchema):
    """Serializer Region fields"""

    class Meta:
        model = Region
        fields = '__all__'


    def validate(self, data):
        region_name = dict(data).get('description')
        region = Region.objects.filter(description=region_name).exists()
        if region:
            raise serializers.ValidationError(['Comarca já cadastrada'])
        return super(RegionSchema, self).validate(data)
