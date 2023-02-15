from base.claim.models import Claim, ClaimCreditor, ClaimLawyer
from rest_framework import serializers

from creditors.classes.schemas import AbstractClassesSchema


class ClaimLawyerSchema(AbstractClassesSchema):
    model = ClaimLawyer

    # classes = None

    class Meta:
        model = ClaimLawyer
        exclude = ('creditor', )


class ClaimCreditorSchema(AbstractClassesSchema):
    model = ClaimCreditor

    class Meta:
        model = ClaimCreditor
        exclude = ('creditor', )


class ClaimSchema(AbstractClassesSchema):
    model = Claim
    creditor_id = None

    class Meta:
        model = Claim
        fields = '__all__'
        # exclude = ('creditor_id', )
