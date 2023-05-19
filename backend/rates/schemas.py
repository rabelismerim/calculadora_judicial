from base.schemas import AbstractDescriptionSchema
from rates.models import Accumulated, Period, Rate, RateFile, RateValues, AbstractCalcule, TemplateField, TemplateRate, \
    Template
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


class RateSchema(AbstractDescriptionSchema):
    """Serializer Rate fields"""

    rate_value = RateValuesSchema(write_only=True)
    rate_values = RateValuesSchema(
        many=True, read_only=True, source='ratevalues_set')

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

    class Meta:
        model = TemplateField
        exclude = ('rate',)


class TemplateRateSchema(AbstractDescriptionSchema):
    """Serializer TemplateRate fields"""

    fields = TemplateFieldSchema(source='templatefield_set', many=True, read_only=True)
    summary = TemplateFieldSchema(source='templatefield_set', many=True, read_only=True)

    class Meta:
        model = TemplateRate
        exclude = ('template',)


class TemplateSchema(AbstractDescriptionSchema):
    """Serializer Template fields"""

    tables = TemplateRateSchema(source='templaterate_set', many=True, read_only=True)
    fields = TemplateFieldSchema(source='templatemainfield_set', many=True, read_only=True)
    class Meta:
        model = Template
        fields = '__all__'


class TemplateListSchema(AbstractDescriptionSchema):
    """Serializer Template fields"""

    class Meta:
        model = Template
        fields = ('id', 'name')
