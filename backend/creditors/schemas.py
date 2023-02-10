from core.abstract.schemas import AbstractModelSchema
from rest_framework import serializers
from core.entity.schemas import EntitySchema
from creditors.models import Creditor
from recovering.schemas import RecoveringSchema


class CreditorSchema(AbstractModelSchema):
    """Serializer Creditor fields"""

    entity = EntitySchema(many=False, read_only=True)
    entity_id = serializers.UUIDField(write_only=True)

    reovering = RecoveringSchema(many=False, read_only=True)
    reovering_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Creditor
        fields = '__all__'
