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

from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers, renderers
from utils import get_user_model
from django.contrib.auth.models import Permission, Group


class PermissionSchema(serializers.ModelSerializer):
    """This class provides a serializers.ModelSerializer subclass to serialize the Permission model fields."""

    class Meta:
        model = Permission
        fields = ['name', 'codename']


class GroupSchema(serializers.ModelSerializer):
    """Serializer for fields of a Group.

    This serializer contains two main fields, name and permissions, along with the extra_kwargs attribute 
    for additional keyword arguments for the field.
    The validate method is responsible for validating the group name and returning either the group's ID 
    if the group exists, or raising a ValidationError if it does not exist.
    """
    permissions = PermissionSchema(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['name', 'permissions', 'id']
        extra_kwargs = {
            'name': {'validators': []},
        }

    def validate(self, data):
        """
        Validate password is strong and same as password confirm.

        Args:
            password (str): Password to validate.
            password_confirm (str): Password confirmation.

        Returns:
            errors (list): List of errors found in validations.
        """
        data = dict(data)
        group = Group.objects.filter(name=data['name']).first()
        if group:
            return super(GroupSchema, self).validate({'id': group.id})
        raise serializers.ValidationError(['Grupo não encontrado'])

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('exclude', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in allowed:
                try:
                    self.fields.pop(field_name)
                except:
                    pass


class UserDttSchema(serializers.ModelSerializer):
    """
    Serializer for fields of the abstract model.

    Attributes:
        renderer_classes (list): A list of JSONRenderer objects.
        id (UUIDField): Unique identifier for the model instance. Read-only.
        password (CharField): Model password with a minimum length of 8 characters. 
                              Write-only, required. 
        password_confirm (CharField): Confirmation of the model's password with a 
                                     minimum length of 8 characters. Write-only, 
                                     required. 
        user_permissions (PermissionSchema): Permissions authorization details associated with model.
                                 Read-only.

        groups (GroupSchema): Groups associated with the model. Read and write access.
    """
    renderer_classes = [renderers.JSONRenderer]
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(
        min_length=8, write_only=True, required=True)
    password_confirm = serializers.CharField(
        min_length=8, write_only=True, required=True)
    user_permissions = PermissionSchema(many=True, read_only=True)
    groups = GroupSchema(many=True, read_only=False, exclude=('permissions', ))
    full_name = serializers.CharField(read_only=True, source='get_full_name')

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'full_name', 'userpicture',
                  'is_staff', 'user_permissions', 'date_joined', 'is_active', 'groups', 'id']
        read_only_fields = ('user_permissions', 'date_joined', 'is_active')

    @staticmethod
    def __check_passwd(password, password_confirm):
        """
        Validate password is strong and same as password confirm.

        Args:
            password (str): Password to validate.
            password_confirm (str): Password confirmation.

        Returns:
            errors (list): List of errors found in validations.
        """
        errors = []

        try:
            validate_password(password=password)
        except exceptions.ValidationError as e:
            errors = list(e.messages)

        if password != password_confirm:
            errors.append('As senhas não correspondem')
        return errors

    def validate(self, data):
        """
        Extends validator method to add custom validators.

        Args:
            data (dict): Data to be validated.

        Raises:
            ValidationError: If validation fails.
        """
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        data['groups'] = [x.get('id') for x in data.get('groups', [])]
        errors = []
        errors.extend(self.__check_passwd(password, password_confirm))
        if errors:
            raise serializers.ValidationError(errors)
        return super(UserDttSchema, self).validate(data)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('exclude', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in allowed:
                try:
                    self.fields.pop(field_name)
                except:
                    pass


class UserAuthorizeDttSchema(serializers.ModelSerializer):
    """
    Serializer for fields of the abstract model.

    Attributes:
        renderer_classes (list): A list of JSONRenderer objects.
    """
    renderer_classes = [renderers.JSONRenderer]

    class Meta:
        model = get_user_model()
        fields = ['email']
