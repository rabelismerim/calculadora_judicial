import re
from base.claim.schemas import ClaimCreditorSchema, ClaimLawyerSchema
from base.coins.models import COIN_CHOICES
from base.schemas import AbstractChoicesSerializer, AbstractDescriptionSchema
from rest_framework import serializers
from core.entity.schemas import EntitySchema
from creditors.classes.models import CLASSE_CHOICES
from creditors.models import Creditor
from creditors.notice.schemas import NoticeSchema, NoticeRecoveringSchema
from rates.schemas import RateSchema


class CreditorSchema(AbstractDescriptionSchema):
    """Serializer Creditor fields"""

    entity = EntitySchema(many=False, read_only=False)

    # recovering = RecoveringSchema(many=False, read_only=True)
    recovering_id = serializers.UUIDField()

    # rate = RateSchema(many=False, read_only=False, exclude=('rate_value', ))
    rate_id = serializers.UUIDField()
    notice_aj = NoticeSchema(source='notice_set', many=True, read_only=False,
                             required=False, allow_null=True, exclude=('creditor_id',))
    notice_recovering = NoticeRecoveringSchema(source='noticerecovering_set', many=True, read_only=False,
                                               required=False, allow_null=True, exclude=('creditor_id',))
    claim_creditor = ClaimCreditorSchema(source='claimcreditor_set',
                                         many=True, read_only=False, required=False, allow_null=True,
                                         exclude=('creditor_id',))
    claim_lawyer = ClaimLawyerSchema(source='claimlawyer',
                                     many=False, read_only=False, required=False, allow_null=True,
                                     exclude=('creditor_id',))

    class Meta:
        model = Creditor
        # fields = '__all__'
        exclude = ('recovering', 'rate')

    def validate(self, data):
        recovering_id = data.get('recovering_id')
        data['notice_recovering'] = data.pop('noticerecovering_set', [])
        data['notice'] = data.pop('notice_set', [])
        data['claim_creditor'] = data.pop('claimcreditor_set', [])
        legal_number = data.get('entity').get('legal_number')
        legal_number = ''.join(re.findall(r'\d', str(legal_number)))

        if Creditor.objects.filter(recovering_id=recovering_id, entity__legal_number=legal_number).exists():
            raise serializers.ValidationError(['Credor já cadastrado nessa recuperanda'])
        return super(CreditorSchema, self).validate(data)


class CreditorCreateSchema(serializers.Serializer):
    """Serializer Creditor fields"""

    classes_options = AbstractChoicesSerializer(
        [{'id': x[0], 'legend': x[1]} for x in CLASSE_CHOICES], many=True, read_only=True)

    coin_options = AbstractChoicesSerializer(
        [{'id': x[0], 'legend': x[1]} for x in COIN_CHOICES], many=True, read_only=True)

    class Meta:
        fields = '__all__'


class CreditorUpdateSchema(AbstractDescriptionSchema):
    """Serializer Creditor fields"""

    class Meta:
        model = Creditor
        fields = ('description', 'admission', 'dismissal', 'default_interest', 'fine', 'advocative_hours')
