from numpy import source
from base.schemas import AbstractDescriptionSchema
from rates.models import Accumulated, Period, Rate, RateValues, AbstractCalcule
from rest_framework import serializers


class AbstractCalcule(AbstractDescriptionSchema):
    """Serializer AbstractCalcule fields"""

    class Meta:
        model = AbstractCalcule
        fields = '__all__'


class PeriodSchema(AbstractDescriptionSchema):
    """Serializer Period fields"""

    class Meta:
        model = Period
        fields = '__all__'
        read_only_fields = ('rate', )


class AccumulatedSchema(AbstractDescriptionSchema):
    """Serializer Accumulated fields"""

    class Meta:
        model = Accumulated
        fields = '__all__'
        read_only_fields = ('rate', )


class RateValuesSchema(AbstractDescriptionSchema):
    """Serializer RateValues fields"""

    # accumulated = AccumulatedSchema(required=False, allow_null=True)
    # period = PeriodSchema(required=False, allow_null=True)

    accumulated = serializers.FloatField(
        required=False, allow_null=True, source='get_accumulated')
    period = serializers.FloatField(
        required=False, allow_null=True, source='get_period')

    class Meta:
        model = RateValues
        # fields = '__all__'
        exclude = ('rate', )

    # def to_representation


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

        rate = Rate.objects.filter(
            index=index_name, ratevalues__date=date).first()

        if rate:
            raise serializers.ValidationError(['Indice já cadastrado'])

        new_rate, created = Rate.objects.get_or_create(index=index_name)

        new_rate_values = RateValues.objects.create(
            rate=new_rate, date=date, value=value)

        if accumulated != None:
            Accumulated.objects.create(
                rate=new_rate_values, value=accumulated)
        if period != None:
            Period.objects.create(
                rate=new_rate_values, value=period)

        return super(RateSchema, self).validate(new_rate)
