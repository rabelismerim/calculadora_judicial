"""
Serializes the fields of the `AbstractModelSchema` model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `AbstractModelSchema` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""
from django_celery_results.models import TaskResult

from core.abstract.models import UpdateUser
from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from base.models import AbstractDescription


class UpdateUserSerializer(serializers.ModelSerializer):
    """
    This serializer creates fields for object UpdateUserSerializer that have an ID and legend associated with them.
    The id field must be a CharField, while the legend field needs to be a CharField of maximum length of 1.
    """

    create_user = serializers.CharField(source='create_user.username')

    class Meta:
        model = UpdateUser
        fields = (
            'created_at', 'field_changed', 'current_value', 'previous_value', 'create_user', 'field_changed_display')


class AbstractDescriptionSchema(serializers.ModelSerializer, AbstractModelSchema):
    """This class uses serializers.ModelSerializer and AbstractModelSchema to serialize the project fields of the
     AbstractDescription model."""

    # TODO V2 ter um get para filtrar pelo id do objeto
    # historical = UpdateUserSerializer(source='get_historical', many=True, read_only=True)
    non_required_fields = []

    class Meta:
        model = AbstractDescription
        fields = '__all__'

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        for field_name in self.non_required_fields:
            if field_name not in extra_kwargs:
                extra_kwargs[field_name] = {'required': False}
            else:
                extra_kwargs[field_name]['required'] = False
        return extra_kwargs


class AbstractChoicesSerializer(serializers.Serializer):
    """
    This serializer creates fields for objects that have an ID and legend associated with them. 
    The id field must be a CharField, while the legend field needs to be a CharField of maximum length of 1.
    """
    id = serializers.CharField()
    legend = serializers.CharField(max_length=1)


class TaskResultSerializer(AbstractDescriptionSchema):
    """
    This serializer creates fields for objects that have an ID and legend associated with them.
    The id field must be a CharField, while the legend field needs to be a CharField of maximum length of 1.
    """
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = TaskResult
        fields = ('task_id', 'status')
        read_only_fields = ('task_id', 'status')
