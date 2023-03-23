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

from calculation.funds.document.models import StatementDocument, MonetaryCorrectionDocument, TotalValuesDocument, \
    FundDocument


class MonetaryCorrectionDocumentSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing MonetaryCorrectionDocuments instances.

    Attributes:
        statement_id (serializers.UUIDField): The UUID of the related statement.
    """
    statement_id = serializers.UUIDField(read_only=True)
    corrected_value = serializers.FloatField(read_only=True)

    class Meta:
        model = MonetaryCorrectionDocument
        exclude = ('statement',)


class StatementDocumentSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementDocuments instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionDocumentSchema(
        read_only=True, source='monetarycorrectiondocument')

    fund_id = serializers.UUIDField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StatementDocument
        exclude = ('fund',)
        read_only_fields = ('status', 'status_display')


class StatementFundDocumentUpdateSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionDocumentSchema(
        read_only=True, source='monetarycorrectiondocument')

    fund_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StatementDocument
        exclude = ('fund',)
        read_only_fields = ('status', 'status_display')
        extra_kwargs = {"data_base": {"required": False, "allow_null": True},
                        "historical_value": {"required": False, "allow_null": True},
                        "number": {"required": False, "allow_null": True},
                        }

    def validate(self, data):
        """
        Validate the given data for the Statement Funds object and raise a `serializers.ValidationError` if any
        validation fails.
        """
        data['status'] = 'S'
        return super(StatementFundDocumentUpdateSchema, self).validate(data)


class TotalValuesDocumentSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    statement = StatementDocumentSchema(
        many=False, source='fund.statementdocument', exclude=('fund_id',), required=False)
    total_days = serializers.IntegerField(read_only=True, source='fund.statementdocument.days')

    class Meta:
        model = TotalValuesDocument
        exclude = ('fund',)


class FundDocumentSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDocumentSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()

    fund = TotalValuesDocumentSchema(source='totalvaluesdocument', read_only=True, exclude=('fund_id',))

    statement = StatementDocumentSchema(source='statementdocument', exclude=('fund_id', 'status'), write_only=True)

    class Meta:
        model = FundDocument
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

        if FundDocument.objects.filter(calculation_id=calculation_id, name=name).exists():
            raise serializers.ValidationError(['Verba já cadastrada'])

        data['statement_document'] = data.pop('statementdocument')
        return super(FundDocumentSchema, self).validate(data)
