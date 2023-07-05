"""
Serializes the fields of the File model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `File` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""
from file.models import File
from base.schemas import AbstractDescriptionSchema, TaskResultSerializer
from rest_framework import serializers


class FileSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the File model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the File
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = FileSchema()
    """
    file_url = serializers.URLField(source='get_file_url', read_only=True)
    # task_result = serializers.CharField(source='get_task_result', read_only=True, allow_null=True)
    # task_id = serializers.UUIDField(source='task_result__id', read_only=True, allow_null=True)

    task = TaskResultSerializer(source='task_result', read_only=True)

    class Meta:
        model = File
        fields = ('file', 'file_url', 'task', 'object_id')
        read_only_fields = ('task_result', 'file_url', 'task_id',)
        write_only_fields = ('file',)
