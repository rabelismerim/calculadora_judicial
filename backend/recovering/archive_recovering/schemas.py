from rest_framework import serializers

from recovering.archive.schemas import ArchiveSchema
from recovering.archive_recovering.models import ArchiveRecovering
from base.schemas import AbstractDescriptionSchema


class ArchiveRecoveringSchema(AbstractDescriptionSchema):

    archive = ArchiveSchema(many=False)
    # archive_id = serializers.UUIDField(write_only=True)

    recovering_id = serializers.UUIDField()

    class Meta:
        model = ArchiveRecovering
        exclude = ('recovering', )
