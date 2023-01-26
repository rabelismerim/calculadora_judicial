from core.abstract.schemas import AbstractModelSchema
from projects.project.models import Project
from rest_framework import serializers
from projects.layer.models import Layer
from projects.abstract_project.schemas import AbstractDescriptionSchema


class LayerSchema(AbstractDescriptionSchema):
    """Serializer Layer fields"""

    class Meta:
        model = Layer
        fields = '__all__'


    def validate(self, data):
        layer_name = dict(data).get('description')
        layer = Layer.objects.filter(description=layer_name).exists()
        if layer:
            raise serializers.ValidationError(['Advogado já cadastrado'])
        return super(LayerSchema, self).validate(data)
