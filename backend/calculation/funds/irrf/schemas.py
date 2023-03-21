"""
Serializes the fields of the Irrf model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Irrf` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""

from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from calculation.funds.irrf.models import StatementIRRF, TotalValuesIRRF


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


class TotalValuesIRRFSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesIRRF instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    funds = StatementIRRFSchema(
        many=True, source='fund.statementirrf_set', exclude=('fund_id',), required=False)

    class Meta:
        model = TotalValuesIRRF
        exclude = ('fund',)
