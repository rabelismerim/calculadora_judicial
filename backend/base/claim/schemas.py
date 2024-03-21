from base.claim.models import Claim, ClaimCreditor, ClaimLawyer
from rest_framework import serializers

from base.schemas import AbstractDescriptionSchema
from calculation.models import Incident
from creditors.classes.schemas import AbstractClassesSchema, AbstractClassesLawyerSchema, AbstractClassesUpdateSchema, \
    AbstractClassesLawyerUpdateSchema


class IncidentSchema(AbstractDescriptionSchema):
    """
    The IncidentSchema class is a serializer for the Incident model fields. It inherits from the AbstractModelSchema class. It includes the following fields:

    creditor: a CreditorSchema instance that is read-only and not serialized.
    creditor_id: a UUIDField instance that is write-only and serialized.
    verdict: a VerdictSchema instance that represents a collection of verdicts related to the Incident.
    criterion: a CriterionSchema instance that is read-only and not serialized.
    funds: a FundsSchema instance that represents a collection of funds related to the Incident.
    statement: a StatementSchema instance that is read-only and not serialized.
    The Meta class is used to specify the Incident model and all fields are serialized.
    The validate method is overridden to handle the verdict_set and funds_set fields and returns the validated data.
    """

    class Meta:
        model = Incident
        fields = '__all__'


class ClaimLawyerSchema(AbstractClassesLawyerSchema):
    model = ClaimLawyer

    class Meta:
        model = ClaimLawyer
        exclude = ('creditor', 'classes')


class ClaimCreditorSchema(AbstractClassesSchema):
    model = ClaimCreditor
    incident_id = serializers.UUIDField(write_only=True)
    incident = IncidentSchema(read_only=True)

    class Meta:
        model = ClaimCreditor
        exclude = ('creditor',)


class ClaimCreditorUpdateSchema(AbstractClassesUpdateSchema):
    model = ClaimCreditor

    class Meta:
        model = ClaimCreditor
        exclude = ('creditor',)


class ClaimLawyerUpdateSchema(AbstractClassesLawyerUpdateSchema):
    model = ClaimCreditor

    class Meta:
        model = ClaimLawyer
        exclude = ('creditor', 'classes')


class ClaimSchema(AbstractClassesSchema):
    model = Claim
    creditor_id = None

    class Meta:
        model = Claim
        fields = '__all__'
        # exclude = ('creditor_id', )
