"""
Registers the Funds, StatementIntegrations, StatementFunds, StatementIRRF, MonetaryCorrection, MonetaryCorrectionIntegrations, TotalValuesIRRF and TotalValuesFunds models with the Django admin site.

This file facilitates the registration of the Funds, StatementIntegrations, StatementFunds, StatementIRRF, MonetaryCorrection, MonetaryCorrectionIntegrations, TotalValuesIRRF and TotalValuesFunds models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the funds.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Funds)
"""

from django.contrib import admin
from calculation.funds.models import Days, Interest, Fine, AmountDue, Funds, StatementIntegrations, StatementFunds, \
    StatementIRRF, StatementDocuments, MonetaryCorrection, MonetaryCorrectionIntegrations, MonetaryCorrectionDocuments, \
    TotalValuesIRRF, TotalValuesFunds, TotalValuesFundsIntegrations, ArrearsCharges

admin.site.register(Days)
admin.site.register(Interest)
admin.site.register(Fine)
admin.site.register(AmountDue)
admin.site.register(Funds)
admin.site.register(StatementIRRF)
admin.site.register(StatementDocuments)
admin.site.register(MonetaryCorrectionDocuments)
admin.site.register(TotalValuesIRRF)
admin.site.register(ArrearsCharges)


class StatementFundsAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = ('corrected_value',)

    @admin.display(description='Valor corrigido')
    def corrected_value(self, model):
        return f'{model.monetarycorrection.corrected_value}'


class StatementFundsIntegrationsAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = ('corrected_value',)

    @admin.display(description='Valor corrigido')
    def corrected_value(self, model):
        return f'{model.monetarycorrectionintegrations.corrected_value}'


class MonetaryCorrectionAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = ('corrected_value',)


class MonetaryCorrectionIntegrationsAdmin(admin.ModelAdmin):
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
    readonly_fields = ('total_corrected', 'total_historical')


class TotalValuesFundsIntegrationsAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = ('total_corrected', 'total_historical')


admin.site.register(MonetaryCorrection, MonetaryCorrectionAdmin)
admin.site.register(MonetaryCorrectionIntegrations, MonetaryCorrectionIntegrationsAdmin)
admin.site.register(StatementFunds, StatementFundsAdmin)
admin.site.register(StatementIntegrations, StatementFundsIntegrationsAdmin)
admin.site.register(TotalValuesFunds, TotalValuesFundsAdmin)
admin.site.register(TotalValuesFundsIntegrations, TotalValuesFundsIntegrationsAdmin)
