"""
Serializes the fields of the Comparative model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Comparative` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

Usage example:
serializer = ComparativeSchema()
"""

from comparative.models import Comparative
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers


class ComparativeSchema(AbstractDescriptionSchema):

    class Meta:
        model = Comparative
        fields = "__all__"
