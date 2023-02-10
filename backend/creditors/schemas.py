import re
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers
from core.entity.schemas import EntitySchema
from creditors.models import Creditor
from recovering.schemas import RecoveringSchema
from rates.schemas import RateSchema


class CreditorSchema(AbstractDescriptionSchema):
    """Serializer Creditor fields"""

    entity = EntitySchema(many=False, read_only=False)

    recovering = RecoveringSchema(many=False, read_only=True)
    recovering_id = serializers.UUIDField(write_only=True)

    rate = RateSchema(many=False, read_only=False)

    class Meta:
        model = Creditor
        fields = '__all__'

    def validate(self, data):
        recovering_id = data.get('recovering_id')
        legal_number = data.get('entity').get('legal_number')
        legal_number = ''.join(re.findall(r'\d', str(legal_number)))

        has_creditor = Creditor.objects.filter(
            recovering_id=recovering_id, entity__legal_number=legal_number).exists()

        if has_creditor:
            raise serializers.ValidationError(
                ['Credor já cadastrado nessa recuperanda'])
        return super(CreditorSchema, self).validate(data)
