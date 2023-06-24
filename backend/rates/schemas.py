from base.schemas import AbstractDescriptionSchema
from rates.models import Accumulated, Period, Rate, RateFile, RateValues, AbstractCalcule, TemplateField, TemplateRate, \
    Template, TemplateSummaryField, TemplateMainSummaryField
from rest_framework import serializers

from utils import _


class AbstractCalculeSchema(AbstractDescriptionSchema):
    """Serializer AbstractCalcule fields"""

    class Meta:
        model = AbstractCalcule
        fields = '__all__'


class PeriodSchema(AbstractDescriptionSchema):
    """Serializer Period fields"""

    class Meta:
        model = Period
        fields = '__all__'
        read_only_fields = ('rate',)


class AccumulatedSchema(AbstractDescriptionSchema):
    """Serializer Accumulated fields"""

    class Meta:
        model = Accumulated
        fields = '__all__'
        read_only_fields = ('rate',)


class RateValuesSchema(AbstractDescriptionSchema):
    """Serializer RateValues fields"""

    accumulated = serializers.FloatField(
        required=False, allow_null=True, source='get_accumulated')
    period = serializers.FloatField(
        required=False, allow_null=True, source='get_period')

    class Meta:
        model = RateValues
        exclude = ('rate',)


class RateValuesCreateSchema(AbstractDescriptionSchema):
    """Serializer for creating RateValues fields.

    This serializer is used to serialize RateValues model data into JSON format for HTTP requests that create new RateValues objects.
    It inherits from the AbstractDescriptionSchema class.

    Attributes:
        accumulated (serializers.FloatField): The accumulated value of the rate, represented as a floating point number.
        period (serializers.FloatField): The period value of the rate, represented as a floating point number.
        rate_id (serializers.UUIDField): The ID of the associated Rate object, used to look up the correct Rate object for the new RateValues object. This field is write-only.
    """

    accumulated = serializers.FloatField(required=False, allow_null=True, source='get_accumulated')
    period = serializers.FloatField(required=False, allow_null=True, source='get_period')

    rate_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = RateValues
        exclude = ('rate',)

    def validate(self, rate_value):
        """
        Validate the input data for creating a new RateValues object.

        This method validates the input data for creating a new RateValues object. It checks if all required data is present,
        creates the necessary related objects (Accumulated and Period) if applicable, and returns the new RateValues object.

        Args:
            rate_value (dict): The dictionary containing the input data for creating a new RateValues object.

        Returns:
            dict: The validated input data dictionary, with any necessary modifications applied.
        """
        accumulated = rate_value.get('get_accumulated', None)
        period = rate_value.get('get_period', None)
        date = rate_value.get('date')
        value = rate_value.get('value')
        rate_id = rate_value.get('rate_id')

        rate = Rate.objects.filter(id=rate_id).first()
        if rate.ratevalues_set.filter(date=date).exists():
            raise serializers.ValidationError([_('Rate date already registered')])

        new_rate_values = RateValues.objects.create(rate=rate, date=date, value=value)

        if accumulated is not None:
            Accumulated.objects.create(rate=new_rate_values, value=accumulated)
        if period is not None:
            Period.objects.create(rate=new_rate_values, value=period)

        return super(RateValuesCreateSchema, self).validate(new_rate_values)


class RateValuesUpdateSchema(AbstractDescriptionSchema):
    """Serializer RateValues fields"""

    accumulated = serializers.FloatField(required=False, allow_null=True, source='get_accumulated')
    period = serializers.FloatField(required=False, allow_null=True, source='get_period')

    class Meta:
        model = RateValues
        exclude = ('rate',)

    def __init__(self, *args, **kwargs):
        super(RateValuesUpdateSchema, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def validate(self, rate_value):
        rate_value['accumulated'] = rate_value.pop('get_accumulated', False)
        rate_value['period'] = rate_value.pop('get_period', False)
        return super(RateValuesUpdateSchema, self).validate(rate_value)

class RateSchema(AbstractDescriptionSchema):
    """Serializer Rate fields"""

    rate_value = RateValuesSchema(write_only=True)
    rate_values = RateValuesSchema(many=True, read_only=True, source='ratevalues_set')

    class Meta:
        model = Rate
        fields = '__all__'

    def validate(self, data):

        data = dict(data)

        index_name = data.get('index')
        rate_value = data.pop('rate_value', None)

        accumulated = rate_value.get('get_accumulated', None)
        period = rate_value.get('get_period', None)
        date = rate_value.get('date')
        value = rate_value.get('value')

        rate = Rate.objects.filter(index=index_name, ratevalues__date=date).first()

        if rate:
            raise serializers.ValidationError([_('Rate already registered')])

        new_rate, created = Rate.objects.get_or_create(index=index_name)

        new_rate_values = RateValues.objects.create(rate=new_rate, date=date, value=value)

        if accumulated is not None:
            Accumulated.objects.create(rate=new_rate_values, value=accumulated)
        if period is not None:
            Period.objects.create(rate=new_rate_values, value=period)

        return super(RateSchema, self).validate(new_rate)


class RateUpdateSchema(AbstractDescriptionSchema):
    """Serializer Rate Update fields"""

    class Meta:
        model = Rate
        fields = ('index', 'is_per_day', 'is_active', 'is_auto_update', 'description', 'periodicity', 'start_date',
                  'end_date')

    def __init__(self, *args, **kwargs):
        super(RateUpdateSchema, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


class RateListSchema(AbstractDescriptionSchema):
    """Serializer Rate list fields"""

    class Meta:
        model = Rate
        fields = ('index', 'is_per_day', 'id')


class RateFileSchema(AbstractDescriptionSchema):
    """Serializer RateFile fields"""
    index = serializers.CharField()
    file = serializers.FileField()

    class Meta:
        model = RateFile
        exclude = ('rate',)


class TemplateFieldSchema(AbstractDescriptionSchema):
    """Serializer TemplateField fields"""

    type_display = serializers.CharField(source='get_type_display')

    default = serializers.SerializerMethodField()
    decimals = serializers.IntegerField()

    def get_default(self, obj):
        return obj.get_default()

    class Meta:
        model = TemplateField
        exclude = ('rate',)


class TemplateSummaryFieldSchema(AbstractDescriptionSchema):
    """Serializer TemplateField fields"""

    type_display = serializers.CharField(source='get_type_display')
    decimals = serializers.IntegerField()

    class Meta:
        model = TemplateSummaryField
        exclude = ('rate',)


class TemplateMainSummaryFieldSchema(AbstractDescriptionSchema):
    """Serializer TemplateField fields"""

    type_display = serializers.CharField(source='get_type_display')
    decimals = serializers.IntegerField()

    class Meta:
        model = TemplateMainSummaryField
        # exclude = ('rate',)
        fields = '__all__'


class TemplateRateSchema(AbstractDescriptionSchema):
    """Serializer TemplateRate fields"""

    fields = TemplateFieldSchema(source='templatefield_set', many=True, read_only=True)
    summary = TemplateSummaryFieldSchema(source='templatesummaryfield_set', many=True, read_only=True)

    class Meta:
        model = TemplateRate
        exclude = ('template',)


class TemplateSchema(AbstractDescriptionSchema):
    """Serializer Template fields"""

    tables = TemplateRateSchema(source='templaterate_set', many=True, read_only=True)
    fields = TemplateFieldSchema(source='templatemainfield_set', many=True, read_only=True)
    summary = TemplateMainSummaryFieldSchema(source='templatemainsummaryfield_set', many=True, read_only=True)

    class Meta:
        model = Template
        fields = '__all__'


class TemplateListSchema(AbstractDescriptionSchema):
    """Serializer Template fields"""

    class Meta:
        model = Template
        fields = ('id', 'name')
