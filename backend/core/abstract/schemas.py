import json
import logging
from json import JSONDecodeError

from rest_framework import serializers, renderers

from base.models import AbstractDescription
from core.abstract.models import UpdateUser
from utils import _


class AbstractModelSchema(serializers.Serializer):
    """Serializer AbstractModel fields"""
    renderer_classes = [renderers.JSONRenderer]
    id = serializers.UUIDField(read_only=True)
    create_user = serializers.CharField(read_only=True)
    update_user = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('exclude', None)
        include_fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            set(self.fields)
            for field_name in allowed:
                try:
                    self.fields.pop(field_name)
                except Exception as e:
                    logging.info(e)

        if include_fields is not None:
            allowed = set(include_fields) & set(self.fields.keys())
            self.fields = {field_name: self.fields[field_name] for field_name in allowed}

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


class AbstractDescriptionSchema(serializers.ModelSerializer, AbstractModelSchema):
    """This class uses serializers.ModelSerializer and AbstractModelSchema to serialize the project fields of the
     AbstractDescription model."""

    # TODO V2 ter um get para filtrar pelo id do objeto
    # historical = UpdateUserSerializer(source='get_historical', many=True, read_only=True)

    class Meta:
        model = AbstractDescription
        fields = '__all__'


class UpdateModelSchema(AbstractDescriptionSchema):
    """Serializer AbstractModel fields"""

    def get_fields(self):
        fields = super(UpdateModelSchema, self).get_fields()
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "PUT":
            for key in fields.keys():
                setattr(fields[key], 'required', False)
        return fields

    class Meta:
        model = UpdateUser
        exclude = ('content_type',)
