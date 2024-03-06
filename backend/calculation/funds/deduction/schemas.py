"""
Serializes the fields of the Document model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Document` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from calculation.funds.deduction.models import StatementDeduction, FundDeduction, StatementDeductionDue
from creditors.classes.schemas import AbstractClassesFundsSchema


class StatementDeductionSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementDeductions instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    data_base = serializers.DateField(required=False, allow_null=True)
    historical_value = serializers.FloatField(required=False, allow_null=True)
    total_legend = serializers.CharField(read_only=True)

    class Meta:
        model = StatementDeduction
        exclude = ('fund',)
        # fields = '__all__'
        read_only_fields = ('status', 'status_display')


class StatementDeductionDueSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementDeductions instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    data_base = serializers.DateField(required=False, allow_null=True)
    historical_value = serializers.FloatField(required=False, allow_null=True)
    total_legend = serializers.CharField(read_only=True)
    total_due = serializers.FloatField(read_only=True)
    historical_charges = serializers.FloatField(read_only=True)

    class Meta:
        model = StatementDeductionDue
        exclude = ('fund',)
        # fields = '__all__'
        read_only_fields = ('status', 'status_display')


class FundDeductionSchema(AbstractClassesFundsSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDeductionSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()
    last_remaining = StatementDeductionSchema(read_only=True, allow_null=True)

    class Meta:
        model = FundDeduction
        exclude = ('calculation',)


class TotalStatementDeductionSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementDeductions instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """

    fund_id = serializers.UUIDField(read_only=True)
    data = StatementDeductionSchema(many=True, source='statementdeduction_set', exclude=('fund_id',), required=False)
    last_remaining = StatementDeductionSchema(read_only=True, allow_null=True)

    class Meta:
        model = FundDeduction
        fields = '__all__'


class TotalStatementDeductionDueSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementDeductions instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """

    fund_id = serializers.UUIDField(read_only=True)
    data = StatementDeductionDueSchema(many=True, source='get_statementdeductiondue', exclude=('fund_id',), required=False)
    total = StatementDeductionDueSchema(many=False, source='statementdeductiondue', exclude=('fund_id',), required=False)

    class Meta:
        model = FundDeduction
        fields = '__all__'
