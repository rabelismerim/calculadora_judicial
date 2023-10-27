"""
Registers the Document models with the Django admin site.

This file facilitates the registration of the Document models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the document.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Document)
"""

from django.contrib import admin

from calculation.funds.admin import AbstractStatementFundsAdmin
from calculation.funds.document.models import StatementDocument, TotalValuesDocument, MonetaryCorrectionDocument, \
    FundDocument
from utils import _

readonly_fields = ['corrected_value', 'index_data_base', 'index_recovering']


class StatementDocumentsAdmin(AbstractStatementFundsAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = readonly_fields + ['days', 'has_tax', 'default_interest', 'fine']
    list_display = ['type']

    def type(self, obj):
        return _('Agreement') if obj.fund.calculation.creditor.physical_person else _('Document')


class FundDocumentAdmin(admin.ModelAdmin):
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
        form = super(FundDocumentAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['rate'].queryset = form.base_fields['rate'].queryset.filter(is_active=True).filter()
        return form


admin.site.register(FundDocument, FundDocumentAdmin)
admin.site.register(TotalValuesDocument)
admin.site.register(StatementDocument, StatementDocumentsAdmin)
admin.site.register(MonetaryCorrectionDocument)
