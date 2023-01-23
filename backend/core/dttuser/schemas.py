from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers, renderers
from utils import get_user_model

class UserDttSchema(serializers.ModelSerializer):
    """Serializer AbstractModel fields"""
    renderer_classes = [renderers.JSONRenderer]
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    password_confirm = serializers.CharField(min_length=8, write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'is_staff']

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
