import re

from base.claim.schemas import ClaimCreditorSchema, ClaimLawyerSchema
from base.coins.models import COIN_CHOICES
from base.models import (CHOICES_CLAIM_TYPE, CHOICES_OCCURRENCE,
                         CHOICES_REPRESENTATION_DOCUMENTATION)
from base.schemas import AbstractDescriptionSchema
from calculation.funds.abstract.models import CHOICES_STATUS_FUND
from calculation.funds.irrf.models import CHOICES_STATUS_IRRF
from calculation.models import CHOICES_STEP
from core.users.models import ROLES_CHOICES, STATUS_CHOICES
from core.entity.schemas import EntitySchema
from creditors.classes.models import CLASSE_CHOICES
from creditors.models import CHOICES_STATUS_LEGAL, Creditor, LegalPendencies
from creditors.notice.schemas import NoticeRecoveringSchema, NoticeSchema
from rates.models import FieldTypeChoices
from recovering.models import Recovering
from rest_framework import serializers
from utils import _, get_legal_number


class LegalPendenciesSchema(AbstractDescriptionSchema):
    """Serializer LegalPendencies fields"""
    creditor_id = serializers.UUIDField()
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = LegalPendencies
        exclude = ('creditor',)


class LegalPendenciesCreditorSchema(AbstractDescriptionSchema):
    """Serializer LegalPendencies fields"""
    creditor_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)

    class Meta:
        model = LegalPendencies
        exclude = ('creditor',)


class LegalPendenciesUpdateSchema(AbstractDescriptionSchema):
    """Serializer LegalPendencies fields"""
    creditor_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True)
    non_required_fields = ['description', 'status']

    class Meta:
        model = LegalPendencies
        exclude = ('creditor',)


class RecoveringDetailSchema(AbstractDescriptionSchema):
    name = serializers.CharField(source='entity.name')
    legal_number = serializers.CharField(source='entity.legal_number')

    class Meta:
        model = Recovering
        fields = ('name', 'legal_number')


class AbstractCreditorSchema(AbstractDescriptionSchema):
    """Serializer Creditor fields"""

    entity = EntitySchema(many=False, read_only=False)

    recovering = RecoveringDetailSchema(many=False, read_only=True)
    recovering_id = serializers.UUIDField()

    # rate = RateSchema(many=False, read_only=False, exclude=('rate_value', ))
    notice_aj = NoticeSchema(source='notice_set', many=True, read_only=False,
                             required=False, allow_null=True, exclude=('creditor_id',))
    notice_recovering = NoticeRecoveringSchema(source='noticerecovering_set', many=True, read_only=False,
                                               required=False, allow_null=True, exclude=('creditor_id',))
    claim_creditor = ClaimCreditorSchema(source='claimcreditor_set', many=True, read_only=False, required=False,
                                         allow_null=True, exclude=('creditor_id',))
    claim_lawyer = ClaimLawyerSchema(source='claimlawyer', many=False, read_only=False, required=False, allow_null=True,
                                     exclude=('creditor_id',))
    legal_pendencies = LegalPendenciesCreditorSchema(
        source='legalpendencies_set', many=True, required=False, allow_null=True)

    calculation_impediment_list = serializers.ListField(
        source='get_calculation_impediment_list', read_only=True)
    nature = serializers.ListField(
        source='get_nature_description', read_only=True, allow_null=True)
    natures = serializers.ListField(
        write_only=True, child=serializers.UUIDField(), required=False, allow_null=True)

    person_type = serializers.ReadOnlyField()

    class Meta:
        model = Creditor
        fields = '__all__'
        # exclude = ('recovering', )
        read_only_fields = ('total',)

    def validate(self, data):
        recovering_id = data.get('recovering_id')
        data['notice_recovering'] = data.pop('noticerecovering_set', [])
        data['notice'] = data.pop('notice_set', [])
        data['claim_creditor'] = data.pop('claimcreditor_set', [])
        data['legal_pendencies'] = data.pop('legalpendencies_set', [])
        legal_number = data.get('entity', {}).get('legal_number')
        legal_number = get_legal_number(legal_number)

        # TODO desbloqueio por classes diferentes
        if Creditor.objects.filter(recovering_id=recovering_id, entity__legal_number=legal_number).exists():
            raise serializers.ValidationError(
                [_('Creditor already registered in this recovering')])
        return super(AbstractCreditorSchema, self).validate(data)


class CreditorSchema(AbstractCreditorSchema):
    """Serializer Creditor fields to create unique Creditor"""
    # rate_id = serializers.UUIDField()


class CreditorRecoveringSchema(AbstractCreditorSchema):
    """Serializer Creditor fields to create unique Creditor"""

    class Meta:
        model = Creditor
        fields = ('id',)


class CreditorBulkSchema(AbstractCreditorSchema):
    """Serializer Creditor fields to create bulk Creditor"""

    # rate_id = serializers.UUIDField(required=False)


class AbstractChoicesSerializer(serializers.Serializer):
    """
    This serializer creates fields for objects that have an ID and legend associated with them.
    The id field must be a CharField, while the legend field needs to be a CharField of maximum length of 1.
    """
    id = serializers.CharField()
    legend = serializers.CharField(max_length=1)

    def to_representation(self, choice):
        return {'id': choice[0], 'legend': choice[1]}


class CreditorCreateSchema(serializers.Serializer):
    """Serializer Creditor fields"""

    classes_options = AbstractChoicesSerializer(CLASSE_CHOICES, many=True)
    coin_options = AbstractChoicesSerializer(COIN_CHOICES, many=True)
    template_type_options = AbstractChoicesSerializer(
        FieldTypeChoices.choices, many=True)
    roles_options = AbstractChoicesSerializer(ROLES_CHOICES, many=True)
    user_status_options = AbstractChoicesSerializer(STATUS_CHOICES, many=True)
    status_funds_options = AbstractChoicesSerializer(
        CHOICES_STATUS_FUND, many=True)
    step_calculation_options = AbstractChoicesSerializer(
        CHOICES_STEP, many=True)
    occurrence_options = AbstractChoicesSerializer(
        CHOICES_OCCURRENCE, many=True)
    status_irrf_options = AbstractChoicesSerializer(
        CHOICES_STATUS_IRRF, many=True)
    status_legal_options = AbstractChoicesSerializer(
        CHOICES_STATUS_LEGAL, many=True)
    representation_document_options = AbstractChoicesSerializer(
        CHOICES_REPRESENTATION_DOCUMENTATION, many=True)
    claim_type_options = AbstractChoicesSerializer(
        CHOICES_CLAIM_TYPE, many=True)

    class Meta:
        fields = '__all__'


class CreditorUpdateSchema(AbstractDescriptionSchema):
    """Serializer Creditor fields"""

    # rate_id = serializers.UUIDField(required=False)
    name = serializers.CharField(source='get_entity_name', read_only=True)
    legal_number = serializers.CharField(
        source='get_entity_legal_number', read_only=True)

    class Meta:
        model = Creditor
        fields = ('description', 'admission', 'dismissal', 'default_interest', 'fine', 'advocative_hours', 'occurrence',
                  'representation_documentation', 'claim_type', 'nature', 'name', 'legal_number')
