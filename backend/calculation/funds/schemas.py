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

from numpy import source
from calculation.funds.models import Funds, StatementFunds, StatementIntegrations
from base.schemas import AbstractDescriptionSchema
from rest_framework import serializers


class StatementFundsSchema(AbstractDescriptionSchema):

    fund_id = serializers.UUIDField()

    class Meta:
        model = StatementFunds
        exclude = ('fund',)


class StatementIntegrationsSchema(AbstractDescriptionSchema):

    fund_id = serializers.UUIDField()

    class Meta:
        model = StatementIntegrations
        exclude = ('fund',)


class FundsSchema(AbstractDescriptionSchema):

    calculation_id = serializers.UUIDField()
    statement_funds = StatementFundsSchema(
        many=True, source='statementfunds_set', exclude=('fund_id', ))

    statement_integrations = StatementIntegrationsSchema(
        many=True, source='statementintegrations_set', exclude=('fund_id', ))

    class Meta:
        model = Funds
        exclude = ('calculation',)

    def validate(self, data):
        name = data.get('name')
        calculation_id = data.get('calculation_id')

        if Funds.objects.filter(calculation_id=calculation_id, name=name).exists():
            raise serializers.ValidationError(['Verba já cadastrada'])

        data['statement_funds'] = data.pop('statementfunds_set', [])
        data['statement_integrations'] = data.pop(
            'statementintegrations_set', [])
        return super(FundsSchema, self).validate(data)
