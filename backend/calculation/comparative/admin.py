"""
Registers the Comparative models with the Django admin site.

This file facilitates the registration of the Comparative models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the comparative.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Comparative)
"""

from django.contrib import admin
from calculation.comparative.models import *
from django.utils.html import format_html
from django.contrib.sites.models import Site


class ComparativeFundsAdmin(admin.ModelAdmin):
    readonly_fields = ('value_dtt', 'difference', 'percentage')


class ComparativeAdmin(admin.ModelAdmin):
    readonly_fields = ('data_base_dtt', 'difference_date')


readonly_fields = [
    'recurral_dtt',
    'recurral_difference',
    'recurral_percentage',

    'total_updated_dtt',
    'total_updated_difference',
    'total_updated_percentage',

    'default_interest_dtt',
    'default_interest_difference',
    'default_interest_percentage',

    'advocative_hours_dtt',
    'advocative_hours_difference',
    'advocative_hours_percentage',

    'total_due_creditor',
    'total_due_dtt',
    'total_due_difference',
    'total_due_percentage',

    'verbas'

]


class AbstractCalculationAdmin(admin.ModelAdmin):
    readonly_fields = readonly_fields

    def recurral_dtt(self, model):
        return f'{model.recurral.dtt}'

    def recurral_difference(self, model):
        return f'{model.recurral.difference}'

    def recurral_percentage(self, model):
        return f'{model.recurral.percentage}'

    def total_updated_dtt(self, model):
        return f'{model.total_updated.dtt}'

    def total_updated_difference(self, model):
        return f'{model.total_updated.difference}'

    def total_updated_percentage(self, model):
        return f'{model.total_updated.percentage}'

    def default_interest_dtt(self, model):
        return f'{model.default_interest.dtt}'

    def default_interest_difference(self, model):
        return f'{model.default_interest.difference}'

    def default_interest_percentage(self, model):
        return f'{model.default_interest.percentage}'

    def advocative_hours_dtt(self, model):
        return f'{model.advocative_hours.dtt}'

    def advocative_hours_difference(self, model):
        return f'{model.advocative_hours.difference}'

    def advocative_hours_percentage(self, model):
        return f'{model.advocative_hours.percentage}'

    readonly_fields = readonly_fields


def get_verbas(comparatives, funds):
    list_href = []
    for comparative in comparatives:
        try:
            domain = Site.objects.get_current().domain
            url = F'{domain}/admin/funds/{funds}/{comparative.total_funds.id}/change/'
            href_certificate = format_html(
                '<a href="{0}" target="_blank">{1}</a>',
                url,
                comparative.total_funds.fund
            )
            list_href.append(href_certificate)
        except Exception as e:
            pass
    return format_html("<br>".join(list_href))


class UpdatedCalculationAdmin(AbstractCalculationAdmin):
    def verbas(self, model):
        comparatives = model.get_comparatives()
        return get_verbas(comparatives, 'totalvaluesfundsintegrations')


class ApprovedCalculationAdmin(AbstractCalculationAdmin):
    def verbas(self, model):
        comparatives = model.get_comparatives()
        return get_verbas(comparatives, 'totalvaluesfunds')


admin.site.register(ComparativeFundsIntegrations)
admin.site.register(RecurralComparative)
admin.site.register(TotalUpdatedComparative)
admin.site.register(DefaultInterestComparative)
admin.site.register(AdvocativeHoursComparative)
admin.site.register(Comparative, ComparativeAdmin)
admin.site.register(ComparativeFunds, ComparativeFundsAdmin)
admin.site.register(ApprovedCalculation, ApprovedCalculationAdmin)
admin.site.register(UpdatedCalculation, UpdatedCalculationAdmin)
