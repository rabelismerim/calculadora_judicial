from datetime import date

from dateutil.relativedelta import relativedelta

from core.abstract.views import AbstractViewApi
from django.http import JsonResponse

from rest_framework import permissions, serializers, status
from core.permission.views import CheckHasPermission
from rates.models import Rate, RateFile, Template, Accumulated, Period, RateValues
from rates.schemas import RateFileSchema, RateSchema, TemplateSchema, TemplateListSchema, RateListSchema, \
    RateUpdateSchema, RateValuesUpdateSchema, RateValuesCreateSchema
from utils import _, doc


class AbstractRateApi(AbstractViewApi):
    """HTTP methods for Rate"""
    serializer_class = RateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Rate

    docs = {
        'init': _("""Represents the indices that can be applied to rates to calculate debt updates.
        """),
        'get': _("""Returns the rate and its accumulated values, period and date""")
    }

    def get_queryset(self):
        return {'is_active': True}


class RateApi(AbstractRateApi):
    """HTTP methods for Rate"""
    http_method_names = ['post', 'get']

    layout_serializers = {
        'default': RateSchema,
        'get': RateListSchema,
        'post': RateSchema,
    }

    query_params = [
        {
            "name": "rate",
            "field": "index__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Rate")),
            "schema": {"type": "string"}
        }
    ]

    @doc(_("""Saves an index according to its name and values"""))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_rate = serializer.validated_data
        return JsonResponse({'rate': self.serializer_class(new_rate, many=False).data}, status=status.HTTP_201_CREATED)


class RateDetailApi(AbstractRateApi):
    """HTTP methods for Rate detail"""
    http_method_names = ['get', 'put']
    layout_serializers = {
        'default': RateSchema,
        'get': RateSchema,
        'put': RateUpdateSchema,
    }


class RateValueDetailApi(AbstractRateApi):
    """HTTP methods for Rate detail"""
    http_method_names = ['post']
    serializer_class = RateValuesCreateSchema
    model = RateValues

    @doc(_("""Saves an rate date according to its name and values"""))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_rate = serializer.validated_data
        return JsonResponse({'rate': self.serializer_class(new_rate, many=False).data}, status=status.HTTP_201_CREATED)


class RateValueDetailUpdateApi(AbstractRateApi):
    """
    A view for updating rate values.

    API endpoint that allows updating of rate values with HTTP PUT requests. Accepts request data in JSON format.

    Methods:
        put(self, request, *args, **kwargs): Method for handling PUT requests to the view.
    """
    http_method_names = ['get', 'put']
    model = RateValues
    layout_serializers = {
        'default': RateValuesCreateSchema,
        'get': RateValuesCreateSchema,
        'put': RateValuesUpdateSchema,
    }

    @doc(_("""The put method in the given code snippet updates rate values stored in the database. Specifically, 
    it updates the accumulated and period fields of a RateValues model object. If the accumulated 
    or period fields have a value of None, the respective object attribute will be deleted if it exists. If 
    the accumulated or period field has a non-null value, the corresponding object attribute will be updated with the 
    new value. If the attribute does not exist, a new Accumulated or Period object will be created with the new value 
    and associated with the appropriate RateValues object. For example, if the request data contains { "date": 
    "2021-08-26", "accumulated": 5.0 }, the accumulated field of the RateValues object will 
    be updated to 5.0. Similarly, if the request data contains { "date": "2021-08-26", "period": 3.0 }, the period 
    field of the RateValues object will be updated to 3.0. It's important to note that the 
    code checks for uniqueness of the date field before updating the RateValues object, so that duplicate entries are 
    not created in the database. If there is already a RateValues object with the same date in the database, 
    the method will raise a serializers.ValidationError with a message indicating that the rate date is already 
    registered."""))
    def put(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_rate = serializer.validated_data

        accumulated = update_rate.pop('accumulated')
        period = update_rate.pop('period')

        rate_date = update_rate.get('date')
        rate_values_id = kwargs.get('id')
        update_rate_values = self.model.objects.filter(id=rate_values_id).first()

        if update_rate_values.rate.ratevalues_set.filter(date=rate_date).exclude(id=rate_values_id).exists():
            raise serializers.ValidationError([_('Rate date already registered')])
        has_accumulated = accumulated in [None, False]
        has_period = period in [None, False]
        if has_accumulated is False:
            if hasattr(update_rate_values, 'accumulated'):
                update_rate_values.accumulated.value = accumulated
                update_rate_values.accumulated.save()
            else:
                Accumulated.objects.create(rate=update_rate_values, value=accumulated)
        elif accumulated is None and hasattr(update_rate_values, 'accumulated'):
            update_rate_values.accumulated.delete()
            update_rate_values.accumulated = None
        if has_period is False:
            if hasattr(update_rate_values, 'period'):
                update_rate_values.period.value = period
                update_rate_values.period.save()
            else:
                Period.objects.create(rate=update_rate_values, value=period)
        elif period is None and hasattr(update_rate_values, 'period'):
            update_rate_values.period.delete()
            update_rate_values.period = None
        update_rate_values.dict_update(**update_rate)
        return JsonResponse({'rate': serializer_class(update_rate_values, many=False).data},
                            status=status.HTTP_201_CREATED)


class RateFileApi(AbstractViewApi):
    """HTTP methods for rate_file"""
    http_method_names = ['post']
    serializer_class = RateFileSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Rate

    query_params = [
        {
            "name": "rate",
            "field": "index__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Rate")),
            "schema": {"type": "string"}
        }
    ]

    @doc(_("""Updating or creating rates through an excel file. Saves an rate using an excel file. This file must contain 
        the columns mes and indice. Optionally according to the rate have the fields acumulado and periodo"""))
    def post(self, request, *args, **kwargs):
        data = request.data
        file = request.FILES.get('file')
        index_name = data.get('index')

        if not index_name:
            raise serializers.ValidationError([_('Required field index')])

        if not file:
            raise serializers.ValidationError([_('Required field file')])

        new_index, created = Rate.objects.get_or_create(index=index_name)
        filename = file.name

        old_file = new_index.get_ratefile()
        if old_file:
            new_file = old_file
        else:
            new_file = RateFile()
            new_file.rate = new_index

        new_file.file.save(file.name, file)
        new_file.save()
        rows = new_file.get_excel_to_dict()

        if rows is False:
            raise serializers.ValidationError(
                [_('The file {} does not contain the correct fields. Required at least the column mes and indice, '
                   f'acumulado and periodo are optional').format(filename)])

        if len(rows) == 0:
            raise serializers.ValidationError(
                [_('The file {} is empty').format(filename)])

        for new_rate in rows:
            serializer = RateSchema(data=new_rate)
            serializer.is_valid(raise_exception=False)

        return JsonResponse({'rate': RateSchema(new_index, many=False).data}, status=status.HTTP_201_CREATED)


class TemplateApi(AbstractViewApi):
    """HTTP methods for Template"""
    http_method_names = ['get']
    serializer_class = TemplateListSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Template

    query_params = [
        {
            "name": "name",
            "field": "name__icontains",
            "in": "query",
            "required": False,
            "description": _("Name"),
            "schema": {"type": "string"}
        }
    ]

    docs = {
        'get': _("""Example of how templates should look for each selected rate type
            Returns a list of templates with their id and name""")
    }


class TemplateDetailApi(AbstractViewApi):
    """HTTP methods for Template"""
    http_method_names = ['get']
    serializer_class = TemplateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Template

    query_params = []

    docs = {
        'get': _("""Example of how templates should look for each selected rate type
        Returns a detail of template with their id, name, tables and fields in tables""")
    }


class TemplateTestEndPointApi(AbstractViewApi):
    """HTTP methods for Template"""
    http_method_names = ['get']
    serializer_class = TemplateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Template

    query_params = []

    docs = {
        'get': _("""Example of how templates should look for each selected rate type
        Returns a detail of template with their id, name, tables and fields in tables""")
    }

    def get(self, request, *args, **kwargs):
        pass

    def _get_index_monetary_correction(self, data: dict) -> dict or None:
        """Retrieves the monetary correction from a financial statement. It gets the calculation, data and rate
        information and then validates the date and rate. The index_data_base and index_recovering are returned as a
        dictionary. """
        data_base: date = data.get('data_base')
        date_rj: date = data.get('date_rj')
        index_name: str = data.get('index')
        summary: bool = data.get('summary')
        value: float = data.get('value')
        dsr: float = data.get('dsr', 0)
        total_historical = value + dsr
        if summary:
            data_base + relativedelta(months=1)
        rate = Rate.objects.filter(index=index_name).first()

        rate_data_base = rate.get_rate_by_date(data_base)
        rate_date_rj = rate.get_rate_by_date(date_rj)

        if not rate_date_rj:
            raise serializers.ValidationError(_('Rate Recovering date not found'))
        if not rate_data_base:
            raise serializers.ValidationError(_('Rate Data Base not found'))

        data = {
            'index_data_base': rate_data_base.value,
            'index_recovering': rate_date_rj.value,
        }

        return data

    def _calc_corrected_value(self, index_recovering: float, index_data_base: float, total_value: float) -> float:
        return index_recovering / index_data_base * total_value

    def corrected_value(self, index_recovering, index_data_base, total_value) -> float:
        """Returns corrected value calculated"""
        return self._calc_corrected_value(index_recovering, index_data_base, total_value)
