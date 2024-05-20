"""
Serializes the fields of the Entity models for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Entity` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""
from rest_framework import serializers
from base.schemas import AbstractDescriptionSchema
from core.entity.models import Entity
from utils import get_legal_number


class EntitySchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the EntitySchema model for use in the API.

    This module defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the EntitySchema
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = EntitySchema()
    """

    class Meta:
        model = Entity
        fields = '__all__'

    def validate_legal_number(self, legal_number):
        """
        This method uses the two validation methods defined earlier to check for either a valid CPF or 
        CNPJ number, as Brazilian law mandates. If neither of those variables are present, then it throws 
        a ValidationError, otherwise it returns the legal number provided.
        """
        return get_legal_number(legal_number)


class EntityCheckSchema(EntitySchema):
    """
    Serializes EntitySchema model fields for use in the API.

    This module defines a Django REST Framework serializer that inherits from a
    AbstractDescriptionSchema class. The serializer converts EntitySchema instances
    model to and from JSON format and validates the received data against the fields in the model. In this model it
    is used to validate the cpf/cnpj field

    Example of use:
    serializer = EntitySchema()
    """
    legal_number = serializers.CharField(validators=[])

    class Meta:
        model = Entity
        fields = ('legal_number',)
