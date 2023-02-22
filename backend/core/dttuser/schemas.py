from unicodedata import name
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers, renderers
from utils import get_user_model
from django.contrib.auth.models import Permission, Group


class PermissionSchema(serializers.ModelSerializer):
    """Serializer Permission fields"""

    class Meta:
        model = Permission
        fields = ['name', 'codename']


class GroupSchema(serializers.ModelSerializer):
    """Serializer Group fields"""
    permissions = PermissionSchema(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        extra_kwargs = {
            'name': {'validators': []},
        }

    def validate(self, data):
        data = dict(data)
        print(data, 'dt\n')
        group = Group.objects.filter(name=data['name']).first()
        if group:
            return super(GroupSchema, self).validate({'id': group.id})
        raise serializers.ValidationError(['Grupo não encontrado'])


class UserDttSchema(serializers.ModelSerializer):
    """Serializer AbstractModel fields"""
    renderer_classes = [renderers.JSONRenderer]
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(
        min_length=8, write_only=True, required=True)
    password_confirm = serializers.CharField(
        min_length=8, write_only=True, required=True)
    user_permissions = PermissionSchema(many=True, read_only=True)
    # groups = GroupSchema(many=True, read_only=False)

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm',
                  'is_staff', 'user_permissions', 'date_joined', 'is_active', 'groups', 'id']
        read_only_fields = ('user_permissions', 'date_joined', 'is_active')

    @staticmethod
    def __check_passwd(password, password_confirm):
        """Validate password is strong and same password confirm"""
        errors = []

        try:
            validate_password(password=password)
        except exceptions.ValidationError as e:
            errors = list(e.messages)

        if password != password_confirm:
            errors.append('As senhas não correspondem')
        return errors

    def validate(self, data):
        """Extend validator method to add custom validators"""
        password = data.get('password')
        password_confirm = data.get('password_confirm')
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
