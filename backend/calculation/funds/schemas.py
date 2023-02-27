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

from calculation.funds.models import Funds, MonetaryCorrection, MonetaryCorrectionIntegrations, StatementFunds, StatementIRRF, StatementIntegrations, TotalValuesFunds, TotalValuesIRRF
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers


class MonetaryCorrectionSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing MonetaryCorrection instances.

    Attributes:
        statement_id (serializers.UUIDField): The UUID of the related statement.
    """
    statement_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = MonetaryCorrection
        exclude = ('statement',)


class MonetaryCorrectionIntegrationsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing MonetaryCorrectionIntegrations instances.

    Attributes:
        statement_id (serializers.UUIDField): The UUID of the related statement.
    """
    statement_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = MonetaryCorrectionIntegrations
        exclude = ('statement',)


class TotalValuesFundsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = TotalValuesFunds
        exclude = ('fund',)


class TotalValuesIRRFSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesIRRF instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = TotalValuesIRRF
        exclude = ('fund',)


class StatementFundsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_corretion = MonetaryCorrectionSchema(
        read_only=True, source='monetarycorrection')

    fund_id = serializers.UUIDField()

    class Meta:
        model = StatementFunds
        exclude = ('fund',)


class StatementIntegrationsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementIntegrations instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_corretion = MonetaryCorrectionIntegrationsSchema(
        read_only=True, source='monetarycorrectionintegrations')
    fund_id = serializers.UUIDField()

    class Meta:
        model = StatementIntegrations
        exclude = ('fund',)


class StatementIRRFSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementIRRF instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField()

    class Meta:
        model = StatementIRRF
        exclude = ('fund',)


class FundsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes:
        calculation_id (serializers.UUIDField): The UUID of the related calculation.
        statement_funds (StatementFundsSchema): The schema for serializing and deserializing StatementFunds instances.
        statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing StatementIntegrations instances.
        statement_irrf (StatementIRRFSchema): The schema for serializing and deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()
    statement_funds = StatementFundsSchema(
        many=True, source='statementfunds_set', exclude=('fund_id', ), required=False)

    statement_integrations = StatementIntegrationsSchema(
        many=True, source='statementintegrations_set', exclude=('fund_id', ), required=False)

    statement_irrf = StatementIRRFSchema(
        many=True, source='statementirrf_set', exclude=('fund_id', ), required=False)

    total_values_funds = TotalValuesFundsSchema(
        source='totalvaluesfunds', read_only=True)
    total_values_irrf = TotalValuesIRRFSchema(
        source='totalvaluesirrf', read_only=True)

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

        Raises:
            serializers.ValidationError: If the validation fails due to any of the following reasons:
                - The Funds object with the given name and calculation_id already exists.
                - Both `statement_irrf` and either of `statement_funds` or `statement_integrations` are present in the data.
                - None of the `statement_funds`, `statement_integrations`, or `statement_irrf` are present in the data.
        """
        name = data.get('name')
        calculation_id = data.get('calculation_id')

        if Funds.objects.filter(calculation_id=calculation_id, name=name).exists():
            raise serializers.ValidationError(['Verba já cadastrada'])

        data['statement_funds'] = data.pop('statementfunds_set', [])
        data['statement_irrf'] = data.pop('statementirrf_set', [])
        data['statement_integrations'] = data.pop(
            'statementintegrations_set', [])

        if (data['statement_funds'] or data['statement_integrations']) and data['statement_irrf']:
            raise serializers.ValidationError(
                ['Verba statement_irrf não pode ser utilizada junto com statement_funds e statement_integrations'])

        if any([data['statement_funds'], data['statement_integrations'], data['statement_irrf']]) is False:
            raise serializers.ValidationError(
                ['Necessário uma verba. Opções: statement_funds, statement_integrations ou statement_irrf'])
        return super(FundsSchema, self).validate(data)
