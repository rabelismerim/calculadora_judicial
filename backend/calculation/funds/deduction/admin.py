"""
Registers the Deduction models with the Django admin site.

This file facilitates the registration of the Deduction models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the document.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Deduction)
"""

from django.contrib import admin

from calculation.funds.admin import AbstractStatementFundsAdmin
from calculation.funds.deduction.models import StatementDeduction, FundDeduction, StatementDeductionRemain

readonly_fields = ['index_data_base', 'index_payment', 'corrected_value', 'days', 'default_interest', 'fine',
                   'remaining_balance']


class StatementDeductionsAdmin(AbstractStatementFundsAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = readonly_fields


class StatementDeductionsRemainAdmin(AbstractStatementFundsAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = readonly_fields


class FundDeductionAdmin(admin.ModelAdmin):
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
        form = super(FundDeductionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['rate'].queryset = form.base_fields['rate'].queryset.filter(is_active=True).filter()
        return form


admin.site.register(FundDeduction, FundDeductionAdmin)
admin.site.register(StatementDeduction, StatementDeductionsAdmin)
admin.site.register(StatementDeductionRemain, StatementDeductionsRemainAdmin)
