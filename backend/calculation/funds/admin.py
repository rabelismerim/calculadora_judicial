"""Registers the Funds, StatementIntegrations, StatementFunds, StatementIRRF, MonetaryCorrection,
MonetaryCorrectionIntegrations, TotalValuesIRRF and TotalValuesFunds models with the Django admin site.

This file facilitates the registration of the Funds, StatementIntegrations, StatementFunds, StatementIRRF,
MonetaryCorrection, MonetaryCorrectionIntegrations, TotalValuesIRRF and TotalValuesFunds models with the Django admin
site. By importing the admin module from the django.contrib package and the relevant models from the funds.models
module, this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Funds)
"""

from django.contrib import admin

from calculation.funds.models import Funds, StatementFunds, MonetaryCorrection, TotalValuesFunds

readonly_fields = ['corrected_value', 'index_data_base', 'index_recovering']


class FundsAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """

    def get_form(self, request, obj=None, **kwargs):
        """
        Customize the form used for the Admin in the Django admin.

        This method filters the 'rate' field queryset based is_active rate.

        Args:
            request (HttpRequest): The current HTTP request object.
            obj (object): The object being edited or None for new objects.
            **kwargs: Additional keyword arguments.
        """
        form = super(FundsAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['rate'].queryset = form.base_fields['rate'].queryset.filter(is_active=True).filter()
        return form


class AbstractStatementFundsAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = readonly_fields

    @admin.display(description='Valor corrigido')
    def corrected_value(self, model):
        return f'{model.get_monetary_correction().corrected_value}'

    @admin.display(description='Índice na data base')
    def index_data_base(self, model):
        return f'{model.get_monetary_correction().index_data_base}'

    @admin.display(description='Índice na recuperanda')
    def index_recovering(self, model):
        return f'{model.get_monetary_correction().index_recovering}'


class StatementFundsAdmin(AbstractStatementFundsAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """


class MonetaryCorrectionAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = ('corrected_value',)


class TotalValuesFundsAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = ('total_corrected', 'total_historical', 'total_dsr_reflexes', 'total_accurate')


admin.site.register(MonetaryCorrection, MonetaryCorrectionAdmin)
admin.site.register(StatementFunds, StatementFundsAdmin)
admin.site.register(TotalValuesFunds, TotalValuesFundsAdmin)
admin.site.register(Funds, FundsAdmin)
