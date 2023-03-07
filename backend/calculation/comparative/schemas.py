"""
Serializes the fields of the Comparative model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Comparative` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

Usage example:
serializer = ComparativeSchema()
"""

from calculation.comparative.models import ApprovedCalculation, Comparative, ComparativeCalculation, ComparativeFunds, ComparativeFundsIntegrations
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers


class ComparativeCalculationSchema(AbstractDescriptionSchema):
    difference = serializers.FloatField()
    percentage = serializers.FloatField()

    class Meta:
        model = ComparativeCalculation
        fields = "__all__"
        read_only_fields = ('dtt', )


class AbstractComparativeFundsSchema(AbstractDescriptionSchema):
    # calculation_id = serializers.UUIDField()
    name = serializers.CharField()
    creditor = serializers.FloatField()
    dtt = serializers.FloatField()
    difference = serializers.FloatField()
    percentage = serializers.FloatField()

    class Meta:
        model = ComparativeFunds
        exclude = ('total_funds', 'calculation')
        read_only_fields = ('dtt', 'difference', 'percentage')


class ComparativeFundsSchema(AbstractComparativeFundsSchema):

    class Meta:
        model = ComparativeFunds
        fields = "__all__"


class ComparativeFundsIntegrationsSchema(AbstractComparativeFundsSchema):

    class Meta:
        model = ComparativeFundsIntegrations
        fields = "__all__"


class TotalDueSchema(serializers.Serializer):
    """
    Serializes the field id of the TotalDueSchema for use in the API.

    Usage example:
    serializer = TotalDueSchema
    """
    creditor = serializers.FloatField()
    dtt = serializers.FloatField()
    difference = serializers.FloatField()
    percentage = serializers.FloatField()


class ApprovedCalculationSchema(AbstractDescriptionSchema):
    recurral = ComparativeCalculationSchema()
    total_updated = ComparativeCalculationSchema()
    default_interest = ComparativeCalculationSchema()
    advocative_hours = ComparativeCalculationSchema()
    total_due = TotalDueSchema(source='get_total_due')

    funds_comparatives = AbstractComparativeFundsSchema(
        source='get_comparatives', many=True)
    funds_comparatives_integrations = AbstractComparativeFundsSchema(
        source='get_comparatives_integrations', many=True)

    class Meta:
        model = ApprovedCalculation
        exclude = ('comparative', )


class ComparativeSchema(AbstractDescriptionSchema):

    approved_calculation = ApprovedCalculationSchema(
        source='approvedcalculation')
    difference_date = serializers.IntegerField()

    class Meta:
        model = Comparative
        read_only_fields = ('approved_calculation', 'difference_date')
        exclude = ('calculation', )
