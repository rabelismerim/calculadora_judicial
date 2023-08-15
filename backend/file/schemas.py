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
from file.models import File, GenericModelPath, ErrorFile
from base.schemas import AbstractDescriptionSchema, TaskResultSerializer
from rest_framework import serializers


class ErrorFileSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the FileErrorSchema model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the FileErrorSchema
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = FileErrorSchema()
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ErrorFile
        fields = ('error', 'status', 'status_display')


class ErrorFileUpdateSchema(ErrorFileSchema):
    """
    Serializes the fields of the FileErrorSchema model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the FileErrorSchema
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = FileErrorSchema()
    """

    class Meta:
        model = ErrorFile
        fields = ('error', 'status', 'status_display')
        non_required_fields = ('status',)
        read_only_fields = ('error',)


class FileSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the File model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the File
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = FileSchema()
    """
    task = serializers.SerializerMethodField(read_only=True)
    errors = ErrorFileSchema(source='errorfile_set', read_only=True, many=True)

    class Meta:
        model = File
        fields = ('id', 'file', 'task', 'object_id', 'errors')
        read_only_fields = ('id', 'task_result', 'task_id', 'errors')
        write_only_fields = ('file',)

    def get_task(self, obj):
        if obj.task_result:
            return TaskResultSerializer(source='task_result').data
        return obj.get_status_pending_task()


class FileListSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the File model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the File
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = FileSchema()
    """

    class Meta:
        model = File
        fields = ('id', 'file')
        read_only_fields = ('id', 'file')


class CharListField(serializers.ListField):
    child = serializers.CharField()


class FileExamplesSchema(serializers.Serializer):
    """
    Serializes the fields of the File model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the File
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = FileSchema()
    """
    excel_names = CharListField()


class BinaryField(serializers.Field):
    def to_representation(self, value):
        return value.decode('utf-8')

    def to_internal_value(self, value):
        return value.encode('utf-8')


class FileBlobExamplesSchema(serializers.Serializer):
    """
    Serializes the fields of the File model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the File
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = FileSchema()
    """
    blob = BinaryField()


class GenericModelPathSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the GenericModelPathSchema model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the GenericModelPathSchema
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = GenericModelPathSchema()
    """

    class Meta:
        model = GenericModelPath
        fields = ('path',)
