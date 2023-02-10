from base.coins.schemas import CoinsSchema
from creditors.classes.schemas import ClassesSchema
from creditors.notice.models import Notice
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers
from creditors.schemas import CreditorSchema

from recovering.archive.schemas import ArchiveJsonSerializer


class NoticeSchema(AbstractDescriptionSchema):

    classes = ClassesSchema(many=False, read_only=False)
    coins = CoinsSchema(many=False, read_only=False)
    archive_json = ArchiveJsonSerializer()
    creditor = CreditorSchema(many=False, read_only=True)
    creditor_id = serializers.UUIDField()

    class Meta:
        model = Notice
        fields = "__all__"

    def validate_creditor_id(self, creditor_id):
        if Notice.objects.filter(creditor_id=creditor_id).exists():
            raise serializers.ValidationError(
                ['Edital já cadastrado para esse credor'])
        return creditor_id
