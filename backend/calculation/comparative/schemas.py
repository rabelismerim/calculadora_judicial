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
    """
    Serializer for the ComparativeCalculation model including difference and percentage fields.

    Attributes:
        difference (FloatField): The difference between the approved calculation and this comparative calculation.
        percentage (FloatField): The percentage difference between the approved calculation and this comparative calculation.

    Meta:
        model (Model): The ComparativeCalculation model to serialize.
        fields (str or list of str): A list of all the fields to be serialized. '__all__' is used to indicate that all fields are included.
        read_only_fields (tuple of str, optional): A tuple of fields to set as read-only. Defaults to ('dtt',).
    """
    difference = serializers.FloatField(read_only=True)
    percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = ComparativeCalculation
        fields = "__all__"
        read_only_fields = ('dtt', )


class AbstractComparativeFundsSchema(AbstractDescriptionSchema):
    """
    A serializer that defines the fields and behavior of ComparativeFunds.

    Required attributes:
        - creditor: The amount of money owed by the debtor.

    Read-only attributes:
        - name: The name of the fund.
        - dtt: The date when the Creditor's recovering request was sent to the DTT.
        - difference: The difference between the creditor and the debtor's requests.
        - percentage: The percentage of the debt based on both the creditor and the debtor's requests.
        - id: The UUID of the instance.

    """
    # calculation_id = serializers.UUIDField()
    name = serializers.CharField(read_only=True)
    creditor = serializers.FloatField()
    dtt = serializers.FloatField(read_only=True)
    difference = serializers.FloatField(read_only=True)
    percentage = serializers.FloatField(read_only=True)
    id = serializers.UUIDField()

    class Meta:
        model = ComparativeFunds
        exclude = ('total_funds', 'calculation')
        read_only_fields = ('dtt', 'difference', 'percentage')


class ComparativeFundsSchema(AbstractComparativeFundsSchema):
    """
    A schema that serializes/deserializes ComparativeFunds objects
    """
    class Meta:
        model = ComparativeFunds
        fields = "__all__"


class ComparativeFundsIntegrationsSchema(AbstractComparativeFundsSchema):
    """
    A schema that serializes/deserializes ComparativeFundsIntegraions objects
    """
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
    dtt = serializers.FloatField(read_only=True)
    difference = serializers.FloatField(read_only=True)
    percentage = serializers.FloatField(read_only=True)


class DatesSchema(serializers.Serializer):
    """
    Serializes the field id of the DatesSchema for use in the API.

    Usage example:
    serializer = DatesSchema
    """
    dtt = serializers.DateField(read_only=True)
    creditor = serializers.DateField()
    difference = serializers.IntegerField(read_only=True)


class ApprovedCalculationSchema(AbstractDescriptionSchema):
    """
    Schema that extends AbstractDescriptionSchema to include approved calculation data such as recurral, 
    total_updated, default_interest, advocative_hours, and funds_comparatives_integrations.
    """
    recurral = ComparativeCalculationSchema(required=False)
    total_updated = ComparativeCalculationSchema(
        required=False, read_only=True)
    default_interest = ComparativeCalculationSchema(required=False)
    advocative_hours = ComparativeCalculationSchema(required=False)
    total_due = TotalDueSchema(source='get_total_due', read_only=True)

    funds_comparatives = AbstractComparativeFundsSchema(required=False,
                                                        source='get_comparatives', many=True)
    funds_comparatives_integrations = AbstractComparativeFundsSchema(required=False,
                                                                     source='get_comparatives_integrations', many=True)

    class Meta:
        model = ApprovedCalculation
        exclude = ('comparative', )

    def validate(self, data):
        """It validates the provided data for serialization and deserialization. It also updates the custom fields."""
        data['funds_comparatives'] = data.pop('get_comparatives', [])
        data['funds_comparatives_integrations'] = data.pop(
            'get_comparatives_integrations', [])
        return super(ApprovedCalculationSchema, self).validate(data)


class ComparativeSchema(AbstractDescriptionSchema):
    """
    The ComparativeSchema class represents a Serializer class for Comparative model. It extends the 
    AbstractDescriptionSchema class and adds custom fields with nested serializers.
    """
    approved_calculation = ApprovedCalculationSchema(
        source='approvedcalculation')
    date = DatesSchema(source='get_dates')

    calculation_id = serializers.UUIDField(read_only=True)

    def validate(self, data):
        """It validates the provided data for serialization and deserialization. It also updates the custom fields."""
        data['approved_calculation'] = data.pop('approvedcalculation', None)
        data['date'] = data.pop('get_dates', None)
        return super(ComparativeSchema, self).validate(data)

    class Meta:
        model = Comparative
        read_only_fields = ('approved_calculation', 'difference_date', 'date')
        exclude = ('calculation', 'data_base_creditor', 'data_base_dtt')
