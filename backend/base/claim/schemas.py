from base.claim.models import Claim, ClaimCreditor, ClaimLawyer
from rest_framework import serializers

from creditors.classes.schemas import AbstractClassesSchema, AbstractClassesLawyerSchema, AbstractClassesUpdateSchema, \
    AbstractClassesLawyerUpdateSchema


class ClaimLawyerSchema(AbstractClassesLawyerSchema):
    model = ClaimLawyer

    class Meta:
        model = ClaimLawyer
        exclude = ('creditor', 'classes')


class ClaimCreditorSchema(AbstractClassesSchema):
    model = ClaimCreditor

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
