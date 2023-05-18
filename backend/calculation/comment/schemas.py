"""
Serializes the fields of the Comment model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Comment` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""

from calculation.comment.models import Comment, StepComment
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers


class CommentSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Comment model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Comment
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = CommentSchema()
    """

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('id',)


class StepCommentSchema(serializers.ModelSerializer):
    """
    Serializes the fields of the StepComment model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Comment
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = StepCommentSchema()
    """
    comments = CommentSchema(many=True)

    class Meta:
        model = StepComment
        exclude = ('calculation',)
