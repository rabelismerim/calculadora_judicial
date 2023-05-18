"""
Registers the Irrf models with the Django admin site.

This file facilitates the registration of the Irrf models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the irrf.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Irrf)
"""

from django.contrib import admin

from calculation.funds.irrf.models import StatementIRRF, TotalValuesIRRF, FundIRRF

admin.site.register(FundIRRF)
admin.site.register(StatementIRRF)


class TotalValuesIRRFAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the TotalValuesIRRF instance.
    """
    readonly_fields = (
        'taxable_amount', 'taxable_portion', 'aliquot', 'installment_deducted', 'irrf_per_month', 'irrf_per_period')


admin.site.register(TotalValuesIRRF, TotalValuesIRRFAdmin)
