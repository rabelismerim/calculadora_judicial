"""
Serializes the fields of the Premise model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Premise` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""
from rest_framework import serializers

from calculation.premise.models import Premise, PremiseValidator
from base.schemas import AbstractDescriptionSchema
from utils import _


class FormulaSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Premise model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Premise
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = PremiseSchema()
    """

    class Meta:
        model = PremiseValidator
        fields = '__all__'


class PremiseSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Premise model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Premise
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = PremiseSchema()
    """

    class Meta:
        model = Premise
        exclude = ('formulas', 'description_en', 'description_pt_br')

    def validate_description(self, description):
        if Premise.objects.filter(description=description).exists():
            raise serializers.ValidationError([_('Premise already registered')])
        return description
