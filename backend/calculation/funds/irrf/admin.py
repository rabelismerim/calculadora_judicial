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


class FundIRRFAdmin(admin.ModelAdmin):
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
        form = super(FundIRRFAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['rate'].queryset = form.base_fields['rate'].queryset.filter(is_active=True).filter()
        return form


admin.site.register(FundIRRF, FundIRRFAdmin)
admin.site.register(StatementIRRF)


class TotalValuesIRRFAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the TotalValuesIRRF instance.
    """
    readonly_fields = (
        'taxable_amount', 'taxable_portion', 'aliquot', 'installment_deducted', 'irrf_per_month', 'irrf_per_period')


admin.site.register(TotalValuesIRRF, TotalValuesIRRFAdmin)
