"""
Serializes the fields of the Funds model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Funds` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.

Usage example:
serializer = FundsSchema()
"""
from calculation.funds.integrations.schemas import StatementIntegrationsSchema, TotalValuesFundsIntegrationsSchema
from calculation.funds.models import Funds, MonetaryCorrection, StatementFunds, TotalValuesFunds
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from utils import _


class MonetaryCorrectionSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing MonetaryCorrection instances.

    Attributes:
        statement_id (serializers.UUIDField): The UUID of the related statement.
    """
    statement_id = serializers.UUIDField(read_only=True)
    corrected_value = serializers.FloatField(read_only=True)

    class Meta:
        model = MonetaryCorrection
        exclude = ('statement',)


class StatementFundsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionSchema(
        read_only=True, source='monetarycorrection')

    fund_id = serializers.UUIDField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StatementFunds
        exclude = ('fund',)
        read_only_fields = ('status', 'status_display')


class StatementFundsUpdateSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionSchema(
        read_only=True, source='monetarycorrection')

    fund_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StatementFunds
        exclude = ('fund',)
        read_only_fields = ('status', 'status_display')
        extra_kwargs = {"data_base": {"required": False, "allow_null": True},
                        "historical_value": {"required": False, "allow_null": True},
                        }

    def validate(self, data):
        """
        Validate the given data for the Statement Funds object and raise a `serializers.ValidationError` if any
        validation fails.
        """
        data['status'] = 'S'
        return super(StatementFundsUpdateSchema, self).validate(data)


class TotalValuesFundsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    funds = StatementFundsSchema(
        many=True, source='fund.statementfunds_set', exclude=('fund_id',), required=False)

    class Meta:
        model = TotalValuesFunds
        exclude = ('fund',)


class FundsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundsSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()

    # statement_funds = StatementFundsSchema(
    #     many=True, source='statementfunds_set', exclude=('fund_id', 'status'), write_only=True, required=False)
    #
    # statement_integrations = StatementIntegrationsSchema(
    #     many=True, source='statementintegrations_set', exclude=('fund_id', 'status'), write_only=True, required=False)

    values_funds = TotalValuesFundsSchema(
        source='totalvaluesfunds', read_only=True, exclude=('fund_id',))

    values_funds_integrations = TotalValuesFundsIntegrationsSchema(
        source='totalvaluesfundsintegrations', read_only=True, exclude=('fund_id',))

    class Meta:
        model = Funds
        exclude = ('calculation',)

    def validate(self, data):
        """
        Validate the given data for the Funds object and raise a `serializers.ValidationError` if any validation fails.

        Args:
            self: The object instance.
            data: A dictionary containing the data to be validated.

        Returns:
            Returns the validated data if all validations pass.

        Raises: serializers.ValidationError: If the validation fails due to any of the following reasons: - The FundIRRF
        object with the given name and calculation_id already exists.
        """
        name = data.get('name')
        calculation_id = data.get('calculation_id')

        if Funds.objects.filter(calculation_id=calculation_id, name=name).exists():
            raise serializers.ValidationError([_('Fund already registered')])

        return super(FundsSchema, self).validate(data)
