"""
Registers the Integrations models with the Django admin site.

This file facilitates the registration of the Integrations models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the integrations.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Integrations)
"""

from django.contrib import admin

from calculation.funds.admin import AbstractStatementFundsAdmin
from calculation.funds.integrations.models import MonetaryCorrectionIntegrations, StatementIntegrations, \
    TotalValuesFundsIntegrations


class StatementFundsIntegrationsAdmin(AbstractStatementFundsAdmin):
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
    readonly_fields = ('total_corrected', 'total_historical', 'total_dsr_reflexes', 'total_accurate')


class TotalValuesFundsIntegrationsAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = ('total_corrected', 'total_historical')


admin.site.register(MonetaryCorrectionIntegrations, MonetaryCorrectionIntegrationsAdmin)
admin.site.register(StatementIntegrations, StatementFundsIntegrationsAdmin)
admin.site.register(TotalValuesFundsIntegrations, TotalValuesFundsIntegrationsAdmin)
