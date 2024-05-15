"""
Serializes the fields of the BigNumber model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `BigNumber` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""
from rest_framework import serializers

from base.schemas import AbstractDescriptionSchema
from core.abstract.schemas import AbstractModelSchema
from projects.models import Project
from utils import _


class MethodField(serializers.SerializerMethodField):
    def __init__(self, method_name=None, label=None, **kwargs):
        # use kwargs for our function instead, not the base class
        super().__init__(method_name)
        self.func_kwargs = kwargs

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        return method(value, **self.func_kwargs)


class BigNumberSchema(AbstractModelSchema):
    """
    Serializes the fields of the BigNumber model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the BigNumber
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = BigNumberSchema()
    """

    def __init__(self, *args, **kwargs):
        bignumber_methods = kwargs.pop('methods_list', [])
        self.request = kwargs.pop('context').get('request')
        super().__init__(*args, **kwargs)

        # Add dynamic fields based on list of BigNumberMethod objects
        for method in bignumber_methods:
            self.fields[method.name] = MethodField(
                method_name='get_method',
                label=method.name,
                method=method.method,
                name=method.name,
                field=getattr(serializers, method.get_field_type_display()),
            )

    def get_method(self, obj, **kwargs):
        method = kwargs.get('method')
        field = kwargs.get('field')
        obj_method = getattr(obj, method, None)

        if not obj_method:
            raise ValueError(_('{} not found').format(method))
        if callable(obj_method):
            try:
                obj_method = obj_method()
            except TypeError:
                obj_method = obj_method(self.request)

        obj_method = field().to_representation(obj_method)
        return obj_method


class CountStatusSchema(AbstractModelSchema):
    status = serializers.CharField(read_only=True)
    total = serializers.IntegerField(read_only=True)


class CountUserSchema(AbstractModelSchema):
    username = serializers.CharField(read_only=True)
    total = serializers.IntegerField(read_only=True)


class BigNumberProjectSchema(AbstractModelSchema):
    count_status = serializers.ListSerializer(child=CountStatusSchema())
    count_users = serializers.ListSerializer(child=CountUserSchema())
