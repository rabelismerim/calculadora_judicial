"""
Registers models from the "rates" app to the Django admin site and defines an action to load data from Excel files for the "RateFile" model.

Functions:
- load_files: Action to load data from an Excel file associated with the selected "RateFile" objects and save the data as instances of the "Rate" model.
- CustomRateFile: Custom admin class for the "RateFile" model that includes the "load_files" action.

Modules:
- django.contrib.admin: Django's built-in administration interface.
- django.contrib.messages: Django's messaging framework.
- rates.models: Models for the "rates" app.
- rates.schemas: Schema for validating data from Excel files.
"""
import json

from django.contrib import admin, messages
from rates.models import Accumulated, Period, Rate, RateValues, RateFile, IndiceIRRF, Template, TemplateRate, \
    TemplateField, TemplateMainField, TemplateMainSummaryField, TemplateSummaryField
from rates.schemas import RateSchema

admin.site.register(Accumulated)
admin.site.register(Period)
admin.site.register(Rate)
admin.site.register(IndiceIRRF)
admin.site.register(Template)
admin.site.register(TemplateRate)
admin.site.register(TemplateField)
admin.site.register(TemplateMainField)
admin.site.register(TemplateSummaryField)
admin.site.register(TemplateMainSummaryField)


def load_files(modeladmin, request, queryset):
    for obj in queryset:
        rows = obj.get_excel_to_dict()

        if rows == False:
            messages.error(
                request,
                f'O arquivo {obj.filename} não contêm os campos corretos. Necessário ao menos a coluna mes e indice, '
                f'acumulado e periodo são opcionais')
            continue

        if len(rows) == 0:
            continue

        index_name = obj.rate.index
        new_rate, created = Rate.objects.get_or_create(index=index_name, is_per_day=obj.rate.is_per_day)
        cont = 0

        rates = Rate.objects.filter(index=index_name)
        rate_values_list = []
        accumulated_values_list = []
        period_values_list = []
        for data in rows:
            rate_value = data.pop('rate_value', None)
            accumulated = rate_value.get('accumulated', None)
            period = rate_value.get('period', None)
            date = rate_value.get('date')
            value = rate_value.get('value')

            if rates.filter(ratevalues__date=date).exists():
                continue

            rate_value = RateValues(rate=new_rate, date=date, value=value)
            rate_values_list.append(rate_value)
            cont += 1
            if accumulated is not None:
                accumulated = Accumulated(rate_id=rate_value.id, value=accumulated)
                accumulated_values_list.append(accumulated)
            if period is not None:
                period = Period(rate_id=rate_value.id, value=period)
                period_values_list.append(period)
        RateValues.objects.bulk_create(rate_values_list)
        Accumulated.objects.bulk_create(accumulated_values_list)
        Period.objects.bulk_create(period_values_list)
        if cont > 0:
            messages.success(
                request, f'Carregado {cont} indice(s) do arquivo {obj.filename}')
        else:
            messages.warning(
                request, f'Nenhum indice carregado do arquivo {obj.filename}')


class AdminRateFile(admin.ModelAdmin):
    actions = [load_files]


class AdminRateValues(admin.ModelAdmin):
    search_fields = ('date',)


admin.site.register(RateFile, AdminRateFile)
admin.site.register(RateValues, AdminRateValues)
