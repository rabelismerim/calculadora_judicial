import json
from rest_framework import serializers
from recovering.archive.models import Archive
from base.schemas import AbstractDescriptionSchema


class ArchiveSchema(AbstractDescriptionSchema):

    archive_json = serializers.JSONField()

    class Meta:
        model = Archive
        fields = "__all__"

    def validate(self, data):
        data = dict(data)
        archive_json = data.get('archive_json')
        if archive_json:
            try:
                file_json = json.loads(archive_json)
            except:
                file_json = archive_json

            if isinstance(file_json, dict) is False:
                raise serializers.ValidationError(
                    ['O campo archive_json é necessário estar no formato json'])
            data['archive_json'] = file_json

        return super(ArchiveSchema, self).validate(data)
