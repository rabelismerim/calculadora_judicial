import json
from json import JSONDecodeError

from rest_framework import serializers, renderers

from utils import _


class AbstractModelSchema(serializers.Serializer):
    """Serializer AbstractModel fields"""
    renderer_classes = [renderers.JSONRenderer]
    id = serializers.UUIDField(read_only=True)
    create_user = serializers.CharField(read_only=True)
    update_user = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(allow_null=True, read_only=True)

    class Meta:
        fields = '__all__'

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

    def validate_archive_json(self, archive_json):
        if archive_json:
            try:
                file_json = json.loads(archive_json)
            except JSONDecodeError:
                file_json = archive_json

            if isinstance(file_json, dict) is False:
                raise serializers.ValidationError([_('The archive_json field must be in json format')])

        return archive_json


class AbstractUpdateModelSchema(AbstractModelSchema):
    """Serializer AbstractModel fields"""

    def get_fields(self):
        fields = super(AbstractUpdateModelSchema, self).get_fields()
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "PUT":
            for key in fields.keys():
                setattr(fields[key], 'required', False)
        return fields
