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

from utils import _


class MethodField(serializers.SerializerMethodField):
    def __init__(self, method_name=None, label=None, **kwargs):
        # use kwargs for our function instead, not the base class
        super().__init__(method_name)
        self.func_kwargs = kwargs

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        return method(value, **self.func_kwargs)


class BigNumberSchema(serializers.Serializer):
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
        name = kwargs.get('name')
        field = kwargs.get('field')
        obj_method = getattr(obj, method, None)

        if not obj_method:
        #     self.fields.pop(name)
            raise ValueError(_('{} not found').format(method))
            return
        if callable(obj_method):
            try:
                obj_method = obj_method()
            except TypeError:
                obj_method = obj_method(self.request)

        obj_method = field().to_representation(obj_method)
        return obj_method

    # def __init__(self, *args, **kwargs):
    #     bignumber_methods = kwargs.pop('methods_list', [])
    #     super().__init__(*args, **kwargs)
    #
    #     # Add dynamic fields based on list of BigNumberMethod objects
    #     for method in bignumber_methods:
    #         field = getattr(serializers, method.get_field_type_display())
    #         self.fields[method.name] = field(source=method.method, label=method.name, context=self.context)
    #
