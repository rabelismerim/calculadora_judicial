from base.schemas import AbstractDescriptionSchema
from core.entity.schemas import EntitySchema
from creditors.schemas import CreditorSchema
from recovering.archive_recovering.schemas import ArchiveRecoveringSchema
from recovering.models import Recovering
from rest_framework import serializers


class RecoveringSchema(AbstractDescriptionSchema):

    entity = EntitySchema(many=False, read_only=False)
    archive = ArchiveRecoveringSchema(
        source='archiverecovering_set', many=True, read_only=True, exclude=('recovering_id', ))
    archives = ArchiveRecoveringSchema(
        many=True, write_only=True, exclude=('recovering_id', ))
    creditors = CreditorSchema(
        source='creditor_set', many=True, read_only=True, allow_null=True)

    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    status_support_display = serializers.CharField(
        source='get_status_support_display', read_only=True)

    project_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Recovering
        # fields = "__all__"
        exclude = ('project', )


class RecoveringListSchema(RecoveringSchema):

    class Meta:
        model = Recovering
        fields = ('id', 'entity')
        # exclude = ('project', )
