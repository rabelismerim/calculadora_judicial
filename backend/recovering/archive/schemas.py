import json
from rest_framework import serializers
from recovering.archive.models import Archive
from base.schemas import AbstractDescriptionSchema


class ArchiveJsonSerializer(serializers.Serializer):
    archive_json = serializers.JSONField()

    def validate_archive_json(self, archive_json):
        if archive_json:
            try:
                file_json = json.loads(archive_json)
            except:
                file_json = archive_json

            if isinstance(file_json, dict) is False:
                raise serializers.ValidationError(
                    ['O campo archive_json é necessário estar no formato json'])

        return archive_json


class ArchiveSchema(AbstractDescriptionSchema):

    # archive_json = ArchiveJsonSerializer()
    archive_json = serializers.JSONField()

    class Meta:
        model = Archive
        fields = "__all__"
