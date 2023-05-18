"""
Serializes the fields of the Integrations model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Integrations` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""

from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from calculation.funds.integrations.models import StatementIntegrations, MonetaryCorrectionIntegrations, \
    TotalValuesFundsIntegrations


class MonetaryCorrectionIntegrationsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing MonetaryCorrectionIntegrations instances.

    Attributes:
        statement_id (serializers.UUIDField): The UUID of the related statement.
    """
    statement_id = serializers.UUIDField(read_only=True)
    corrected_value = serializers.FloatField(read_only=True)

    class Meta:
        model = MonetaryCorrectionIntegrations
        exclude = ('statement',)


class StatementIntegrationsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementIntegrations instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionIntegrationsSchema(
        read_only=True, source='monetarycorrectionintegrations')
    fund_id = serializers.UUIDField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StatementIntegrations
        exclude = ('fund',)
        read_only_fields = ('status', 'status_display')


class StatementIntegrationsUpdateSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementIntegrations instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionIntegrationsSchema(
        read_only=True, source='monetarycorrectionintegrations')
    fund_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StatementIntegrations
        exclude = ('fund',)
        read_only_fields = ('status', 'status_display')
        extra_kwargs = {"data_base": {"required": False, "allow_null": True},
                        "historical_value": {"required": False, "allow_null": True},
                        "description": {"required": False, "allow_null": True}
                        }

    def validate(self, data):
        """
        Validate the given data for the Statement Funds object and raise a `serializers.ValidationError` if any
        validation fails.
        """
        data['status'] = 'S'
        return super(StatementIntegrationsUpdateSchema, self).validate(data)


class TotalValuesFundsIntegrationsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesFundsIntegrations instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    funds = StatementIntegrationsSchema(
        many=True, source='fund.statementintegrations_set', exclude=('fund_id',), required=False)

    class Meta:
        model = TotalValuesFundsIntegrations
        exclude = ('fund',)
