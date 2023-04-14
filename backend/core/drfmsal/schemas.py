"""
Serializes the fields of the Statement model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Statement` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

Usage example:
serializer = StatementSchema()
"""

from rest_framework import serializers
from rest_framework.fields import DictField


class CustomDictField(DictField):
    pass


class ProfileSerializer(serializers.Serializer):
    """Serializer for the SignStatus object, which represents the sign status of a user."""
    authorized = serializers.BooleanField()
    authenticated = serializers.BooleanField()
    user_fullname = serializers.CharField()
    profile = serializers.URLField()


class SignStatusSerializer(serializers.Serializer):
    """Serializer for the SignStatus object, which represents the sign status of a user."""
    data = CustomDictField()
    dttdjud = serializers.BooleanField()
    accept_token = serializers.BooleanField()
    profile = ProfileSerializer()
