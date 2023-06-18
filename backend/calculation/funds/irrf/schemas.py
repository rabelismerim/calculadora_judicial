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

from calculation.funds.irrf.models import StatementIRRF, TotalValuesIRRF, FundIRRF
from creditors.classes.schemas import AbstractClassesFundsSchema
from utils import _


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
        read_only_fields = ('status', 'status_display')


class StatementIRRFUpdateSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementIntegrations instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = StatementIRRF
        exclude = ('fund',)
        read_only_fields = ('status', 'status_display')
        extra_kwargs = {"taxable_amounts": {"required": False, "allow_null": True},
                        "fund_name": {"required": False, "allow_null": True},
                        }


class TotalValuesIRRFSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesIRRF instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    data = StatementIRRFSchema( many=True, source='fund.statementirrf_set', exclude=('fund_id',), required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TotalValuesIRRF
        exclude = ('fund',)

    def validate(self, data):
        """
        Validate the given data for the TotalValuesIRRF object and raise a `serializers.ValidationError` if any
        validation fails.
        """
        data['status'] = 'S'
        return super(TotalValuesIRRFSchema, self).validate(data)


class FundIRRFSchema(AbstractClassesFundsSchema):
    """
    A schema for serializing and deserializing FundIRRF instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundIRRFSchema): The schema for serializing and deserializing StatementFundIRRF instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()
    # values_funds = TotalValuesIRRFSchema(
        # source='totalvaluesirrf', read_only=True, exclude=('fund_id',))

    class Meta:
        model = FundIRRF
        exclude = ('calculation', )

    def validate(self, data):
        """
        Validate the given data for the FundIRRF object and raise a `serializers.ValidationError` if any validation fails.

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

        if FundIRRF.objects.filter(calculation_id=calculation_id, name=name).exists():
            raise serializers.ValidationError([_('Fund already registered')])

        return super(FundIRRFSchema, self).validate(data)
