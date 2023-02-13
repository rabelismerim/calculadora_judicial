from base.claim.models import ClaimCreditor, ClaimLawyer
from rest_framework import serializers

from creditors.classes.schemas import AbstractClassesSchema


class ClaimLawyerSchema(AbstractClassesSchema):
    model = ClaimLawyer

    classes = None

    class Meta:
        model = ClaimLawyer
        exclude = ('creditor', )


class ClaimCreditorSchema(AbstractClassesSchema):
    model = ClaimCreditor

    class Meta:
        model = ClaimCreditor
        exclude = ('creditor', )
