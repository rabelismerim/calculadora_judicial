import logging

from rest_framework import serializers

from core.users.models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('exclude', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            set(self.fields)
            for field_name in allowed:
                try:
                    self.fields.pop(field_name)
                except KeyError as e:
                    logging.info(e)
