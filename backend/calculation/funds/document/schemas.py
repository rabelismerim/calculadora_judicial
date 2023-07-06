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
from creditors.classes.schemas import AbstractClassesFundsSchema
from utils import _


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
    monetary_correction = MonetaryCorrectionDocumentSchema(read_only=True, source='monetarycorrectiondocument')

    fund_id = serializers.UUIDField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    historical_value = serializers.FloatField()
    data_base = serializers.DateField()
    is_extraconcursal = serializers.BooleanField()
    number = serializers.CharField()

    class Meta:
        model = StatementDocument
        exclude = ('fund',)
        # fields = '__all__'
        read_only_fields = ('status', 'status_display')


class StatementDocumentUpdateSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementDocuments instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionDocumentSchema(read_only=True, source='monetarycorrectiondocument')

    fund_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    data_base = serializers.DateField(required=False)
    historical_value = serializers.FloatField(required=False)
    number = serializers.CharField(required=False)

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
    data = StatementDocumentSchema(many=False, source='fund.statementdocument', exclude=('fund_id',), required=False)
    total_days = serializers.IntegerField(read_only=True, source='fund.statementdocument.days')

    class Meta:
        model = TotalValuesDocument
        # exclude = ('id',)
        fields = '__all__'


class FundDocumentDetailSchema(AbstractClassesFundsSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDocumentSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()

    class Meta:
        model = FundDocument
        exclude = ('calculation',)


class TotalValuesDocumentDetailSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    data = StatementDocumentSchema(many=False, source='fund.statementdocument', exclude=('fund_id',), required=False)
    total_days = serializers.IntegerField(read_only=True, source='fund.statementdocument.days')
    fund = FundDocumentDetailSchema(many=False)

    # def get_data(self, obj):
    #     print(obj, 'obj\n' )
    #     statement_document = obj.fund.statementdocument
    #     return StatementDocumentSchema(instance=statement_document).data
    #
    # def to_representation(self, instance):
    #     print(instance, 'instance\n')
    #     representation = super().to_representation(instance)
    #     representation.pop('fund_id', None)  # Remover a chave 'fund_id' do dicionário
    #     return representation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        statement_document = representation.pop('fund', {})
        for key, value in statement_document.items():
            representation[key] = value
        statement_document = representation.pop('data', {})
        for key, value in statement_document.items():
            representation[key] = value
        monetary_correction = representation.pop('monetary_correction', {})
        for key, value in monetary_correction.items():
            representation[key] = value
        return representation

    class Meta:
        model = TotalValuesDocument
        # exclude = ('id',)
        fields = '__all__'


class FundDocumentSchema(AbstractClassesFundsSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDocumentSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()
    total = TotalValuesDocumentSchema(source='totalvaluesdocument', read_only=True, exclude=('fund_id', 'statement'))
    statement = StatementDocumentSchema(source='statementdocument', exclude=('fund_id', 'status'), read_only=True)
    commit = serializers.BooleanField(write_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        statement_serializer = StatementDocumentSchema(exclude=('fund_id', 'status'))
        statement_fields = statement_serializer.get_fields()
        self.write_only_fields = {}
        extra_kwargs = {}
        for field_name, field in statement_fields.items():
            in_exclude = field_name in ['fund_id', 'status']
            if not in_exclude and field.read_only is False:
                field.write_only = True
                extra_kwargs[field_name] = {'write_only': True}
                self.write_only_fields[field_name] = field

        StatementDocumentSchema.Meta.extra_kwargs = extra_kwargs
        self.fields.update(self.write_only_fields)

    class Meta:
        model = FundDocument
        exclude = ('calculation',)


class FundDocumentGetSchema(AbstractClassesFundsSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDocumentSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()
    total = TotalValuesDocumentSchema(source='totalvaluesdocument', read_only=True, exclude=('fund_id', 'statement'))

    # statement = StatementDocumentSchema(source='statementdocument', exclude=('fund_id', 'status'), read_only=True)

    class Meta:
        model = FundDocument
        exclude = ('calculation',)


class FundDocumentUpdateSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDocumentSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField(read_only=True)
    fund = TotalValuesDocumentSchema(source='totalvaluesdocument', read_only=True, exclude=('fund_id',))
    statement = StatementDocumentUpdateSchema(source='statementdocument', exclude=('fund_id', 'status'),
                                              write_only=True, required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = FundDocument
        exclude = ('calculation', 'rate')

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
        data['statement_document'] = data.pop('statementdocument', None)
        return super(FundDocumentUpdateSchema, self).validate(data)
