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

from calculation.funds.models import AbstractValue, AmountDue, ArrearsCharges, Days, Fine, Funds, Interest, \
    MonetaryCorrection, MonetaryCorrectionDocuments, MonetaryCorrectionIntegrations, StatementDocuments, StatementFunds, \
    StatementIRRF, StatementIntegrations, TotalValuesFunds, TotalValuesFundsIntegrations, TotalValuesIRRF
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


class MonetaryCorrectionDocumentsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing MonetaryCorrectionDocuments instances.

    Attributes:
        statement_id (serializers.UUIDField): The UUID of the related statement.
    """
    statement_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = MonetaryCorrectionDocuments
        exclude = ('statement',)


class AbstractValueSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing AbstractValue instances.

    Attributes:
        arrears_charges_id (serializers.UUIDField): The UUID of the related arrears_charges.
    """
    arrears_charges_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = AbstractValue
        exclude = ('arrears_charges',)


class DaysSchema(AbstractValueSchema):
    """
    A schema for serializing and deserializing Days instances.

    Attributes:
        arrears_charges_id (serializers.UUIDField): The UUID of the related arrears_charges.
    """
    arrears_charges_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Days
        exclude = ('arrears_charges',)


class InterestSchema(AbstractValueSchema):
    """
    A schema for serializing and deserializing Interest instances.

    Attributes:
        arrears_charges_id (serializers.UUIDField): The UUID of the related arrears_charges.
    """
    arrears_charges_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Interest
        exclude = ('arrears_charges',)


class FineSchema(AbstractValueSchema):
    """
    A schema for serializing and deserializing Fine instances.

    Attributes:
        arrears_charges_id (serializers.UUIDField): The UUID of the related arrears_charges.
    """
    arrears_charges_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Fine
        exclude = ('arrears_charges',)


class AmountDueSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing AmountDue instances.

    Attributes:
        arrears_charges_id (serializers.UUIDField): The UUID of the related arrears_charges.
    """
    statement_document_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = AmountDue
        exclude = ('statement_document',)


class ArrearsChargesSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing ArrearsCharges instances.

    Attributes:
        statement_id (serializers.UUIDField): The UUID of the related statement.
    """
    statement_id = serializers.UUIDField(
        read_only=True)
    days = DaysSchema(read_only=True, exclude=('arrears_charges_id',))
    interest = InterestSchema(read_only=True, exclude=('arrears_charges_id',))
    fine = FineSchema(read_only=True, exclude=('arrears_charges_id',))

    class Meta:
        model = ArrearsCharges
        exclude = ('statement',)


class StatementFundsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_corretion = MonetaryCorrectionSchema(
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
    monetary_corretion = MonetaryCorrectionSchema(
        read_only=True, source='monetarycorrection')

    fund_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StatementFunds
        exclude = ('fund',)
        read_only_fields = ('status', 'status_display')


class StatementIntegrationsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementIntegrations instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_corretion = MonetaryCorrectionIntegrationsSchema(
        read_only=True, source='monetarycorrectionintegrations')
    fund_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StatementIntegrations
        exclude = ('fund',)
        read_only_fields = ('status', 'status_display')


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


class StatementDocumentsSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementDocuments instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    amount_due = AmountDueSchema(
        read_only=True, source='amountdue', exclude=('statement_document_id',))
    arrears_charges = ArrearsChargesSchema(
        read_only=True, source='arrearscharges', exclude=('statement_id',))
    monetary_corretion = MonetaryCorrectionDocumentsSchema(
        read_only=True, source='monetarycorrectiondocuments', exclude=('statement_id',))

    class Meta:
        model = StatementDocuments
        exclude = ('fund',)


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
        many=True, source='statementfunds_set', exclude=('fund_id', 'status'), write_only=True, required=False)

    statement_integrations = StatementIntegrationsSchema(
        many=True, source='statementintegrations_set', exclude=('fund_id', 'status'), write_only=True, required=False)

    statement_irrf = StatementIRRFSchema(
        many=True, source='statementirrf_set', exclude=('fund_id',), write_only=True, required=False)

    statement_documents = StatementDocumentsSchema(
        source='statementdocuments', exclude=('fund_id',), write_only=True, required=False)

    values_funds_documents = StatementDocumentsSchema(
        source='statementdocuments', exclude=('fund_id',), read_only=True)

    values_funds = TotalValuesFundsSchema(
        source='totalvaluesfunds', read_only=True, exclude=('fund_id',))

    values_funds_integrations = TotalValuesFundsIntegrationsSchema(
        source='totalvaluesfundsintegrations', read_only=True, exclude=('fund_id',))

    values_irrf = TotalValuesIRRFSchema(
        source='totalvaluesirrf', read_only=True, exclude=('fund_id',))

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
        data['statement_documents'] = data.pop('statementdocuments', {})
        data['statement_integrations'] = data.pop(
            'statementintegrations_set', [])

        is_funds = True if data['statement_funds'] or data['statement_integrations'] else False
        is_irrf = True if data['statement_irrf'] else False
        is_documents = True if data['statement_documents'] else False
        if [is_funds, is_irrf, is_documents].count(True) > 1:
            raise serializers.ValidationError(
                [
                    'Utilização de verbas inválidas. Utilizar separadamente as verbas (statement_funds e statement_integrations) ou statement_irrf ou statement_documents'])

        if any([data['statement_funds'], data['statement_integrations'], data['statement_irrf'],
                data['statement_documents']]) is False:
            raise serializers.ValidationError(
                [
                    'Necessário uma verba. Opções: statement_funds, statement_integrations, statement_irrf, ou statement_documents'])

        return super(FundsSchema, self).validate(data)
