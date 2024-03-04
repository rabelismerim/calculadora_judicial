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

from calculation.funds.danos.models import StatementDanos, MonetaryCorrectionDanos, TotalValuesDanos, \
    FundDanos, InterestChoices
from creditors.classes.schemas import AbstractClassesFundsSchema
from utils import _


class MonetaryCorrectionDanosSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing MonetaryCorrectionDanoss instances.

    Attributes:
        statement_id (serializers.UUIDField): The UUID of the related statement.
    """
    statement_id = serializers.UUIDField(read_only=True)
    corrected_value = serializers.FloatField(read_only=True)

    class Meta:
        model = MonetaryCorrectionDanos
        exclude = ('statement',)


class StatementDanosSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementDanos instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionDanosSchema(read_only=True, source='monetarycorrectiondanos')

    fund_id = serializers.UUIDField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    historical_value = serializers.FloatField()
    data_base = serializers.DateField()
    description = serializers.CharField()
    total_days = serializers.IntegerField(read_only=True)
    total_default_interest = serializers.FloatField(source='default_interest', read_only=True)

    # default_interest = serializers.FloatField(source='default_interest', read_only=True)

    class Meta:
        model = StatementDanos
        exclude = ('fund', 'is_extraconcursal')
        # fields = '__all__'
        read_only_fields = ('status', 'status_display')


class StatementDanosUpdateSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementDanos instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionDanosSchema(read_only=True, source='monetarycorrectiondanos')

    fund_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    data_correction = serializers.DateField(required=False)
    historical_value = serializers.FloatField(required=False)
    description = serializers.CharField(required=False)
    interest_initial_date = serializers.DateField(write_only=True, required=False)
    apply_monetary_correction = serializers.BooleanField(write_only=True, required=False)
    type_interest = serializers.ChoiceField(choices=InterestChoices.choices, write_only=True, required=False)
    description_correction = serializers.CharField(required=False)

    class Meta:
        model = StatementDanos
        exclude = ('fund', 'is_extraconcursal')
        read_only_fields = ('status', 'status_display')


class StatementFundDanosUpdateSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing StatementFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    monetary_correction = MonetaryCorrectionDanosSchema(
        read_only=True, source='monetarycorrectiondanos')

    fund_id = serializers.UUIDField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StatementDanos
        exclude = ('fund', 'is_extraconcursal')
        read_only_fields = ('status', 'status_display')
        extra_kwargs = {"data_base": {"required": False, "allow_null": True},
                        "historical_value": {"required": False, "allow_null": True},
                        "description": {"required": False, "allow_null": True},
                        }

    def validate(self, data):
        """
        Validate the given data for the Statement Funds object and raise a `serializers.ValidationError` if any
        validation fails.
        """
        data['status'] = 'S'
        return super(StatementFundDanosUpdateSchema, self).validate(data)


class TotalValuesDanosSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    data = StatementDanosSchema(many=False, source='fund.statementdanos', exclude=('fund_id',), required=False)
    total_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = TotalValuesDanos
        # exclude = ('id',)
        fields = '__all__'


class FundDanosDetailSchema(AbstractClassesFundsSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDanosSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()

    class Meta:
        model = FundDanos
        exclude = ('calculation',)


class TotalValuesDanosDetailSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing TotalValuesFunds instances.

    Attributes:
        fund_id (serializers.UUIDField): The UUID of the related fund.
    """
    fund_id = serializers.UUIDField(read_only=True)
    data = StatementDanosSchema(many=False, source='fund.statementdanos', exclude=('fund_id',), required=False)
    total_days = serializers.IntegerField(read_only=True)
    fund = FundDanosDetailSchema(many=False)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        new_fund = {
            'total_days': representation.get('total_days', 0),
            'total_fine': representation.get('total_fine', 0),
            'total_due': representation.get('total_due', 0),
            'total_default_interest': representation.get('total_default_interest', 0),
        }
        statement_danos = representation.pop('fund', {})

        if statement_danos:
            for key, value in statement_danos.items():
                new_fund[key] = value

        data = representation.pop('data', {})
        if data:
            for key, value in data.items():
                if key == 'id':
                    key = 'fund_id'
                new_fund[key] = value
        monetary_correction = new_fund.get('monetary_correction', {})
        if monetary_correction:
            for key, value in monetary_correction.items():
                if key == 'id':
                    key = 'monetary_correction_id'
                new_fund[key] = value

        representation['data'] = [new_fund]
        return representation

    class Meta:
        model = TotalValuesDanos
        # exclude = ('id',)
        fields = '__all__'


class FundDanosSchema(AbstractClassesFundsSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDanosSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()
    total = TotalValuesDanosSchema(source='totalvaluesdanos', read_only=True, exclude=('fund_id', 'statement'))
    statement = StatementDanosSchema(source='statementdanos', exclude=('fund_id', 'status'), read_only=True)
    commit = serializers.BooleanField(write_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        statement_serializer = StatementDanosSchema(exclude=('fund_id', 'status'))
        statement_fields = statement_serializer.get_fields()
        self.write_only_fields = {}
        extra_kwargs = {}
        for field_name, field in statement_fields.items():
            in_exclude = field_name in ['fund_id', 'status']
            if not in_exclude and field.read_only is False:
                field.write_only = True
                extra_kwargs[field_name] = {'write_only': True}
                self.write_only_fields[field_name] = field

        StatementDanosSchema.Meta.extra_kwargs = extra_kwargs
        self.fields.update(self.write_only_fields)

    class Meta:
        model = FundDanos
        exclude = ('calculation',)

    def validate(self, data):
        """
        Validate the given data for the Funds object and raise a `serializers.ValidationError` if any validation fails.

        Args:
            self: The object instance.
            data: A dictionary containing the data to be validated.

        :return:
            Returns the validated data if all validations pass.

        Raises: serializers.ValidationError: If the validation fails due to any of the following reasons: - The FundIRRF
        object with the given name and calculation_id already exists.
        """
        name = data.get('name')
        data_base = data.get('data_base')
        description = data.get('description')
        historical_value = data.get('historical_value')
        calculation_id = data.get('calculation_id')

        if FundDanos.objects.filter(calculation_id=calculation_id, name=name, statementdanos__data_base=data_base,
                                    statementdanos__description=description,
                                    statementdanos__historical_value=historical_value).exists():
            raise serializers.ValidationError([_('Verba de dano já registrada')])
        data['statement_danos'] = {}
        for field_name in self.write_only_fields.keys():
            data['statement_danos'][field_name] = data.pop(field_name)
        return super(FundDanosSchema, self).validate(data)


class FundDanosGetSchema(AbstractClassesFundsSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDanosSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField()
    total = TotalValuesDanosSchema(source='totalvaluesdanos', read_only=True, exclude=('fund_id', 'statement'))

    class Meta:
        model = FundDanos
        exclude = ('calculation',)


class FundDanosUpdateSchema(AbstractDescriptionSchema):
    """
    A schema for serializing and deserializing Funds instances.

    Attributes: calculation_id (serializers.UUIDField): The UUID of the related calculation. statement_funds (
    StatementFundDanosSchema): The schema for serializing and deserializing StatementFunds instances.
    statement_integrations (StatementIntegrationsSchema): The schema for serializing and deserializing
    StatementIntegrations instances. statement_irrf (StatementIRRFSchema): The schema for serializing and
    deserializing StatementIRRF instances.
    """
    calculation_id = serializers.UUIDField(read_only=True)
    fund = TotalValuesDanosSchema(source='totalvaluesdanos', read_only=True, exclude=('fund_id',))
    statement = StatementDanosUpdateSchema(source='statementdanos', exclude=('fund_id', 'status'),
                                           write_only=True, required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = FundDanos
        exclude = ('calculation', 'rate')

    def validate(self, data):
        """
        Validate the given data for the Funds object and raise a `serializers.ValidationError` if any validation fails.

        Args:
            self: The object instance.
            data: A dictionary containing the data to be validated.

        :return:
            Returns the validated data if all validations pass.

        Raises: serializers.ValidationError: If the validation fails due to any of the following reasons: - The FundIRRF
        object with the given name and calculation_id already exists.
        """
        data['statement_danos'] = data.pop('statementdanos', None)
        return super(FundDanosUpdateSchema, self).validate(data)
