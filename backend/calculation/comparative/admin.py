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
import logging

from django.contrib import admin
from calculation.comparative.models import *
from django.utils.html import format_html
from django.contrib.sites.models import Site

readonly_fields_funds = ('system', 'difference', 'percentage')


class ComparativeFundsAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the ComparativeFunds instance.
    """
    readonly_fields = readonly_fields_funds


class ComparativeFundsIntegrationsAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the ComparativeFundsIntegrations instance.
    """
    readonly_fields = readonly_fields_funds


class ComparativeAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the Comparative instance.
    """
    readonly_fields = ('data_base_system', 'difference_date')


class ComparativeCalculationAdmin(admin.ModelAdmin):
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the ComparativeCalculation instance.
    """
    readonly_fields = ('system',)


readonly_fields = [
    'recurral_system',
    'recurral_difference',
    'recurral_percentage',

    'total_updated_system',
    'total_updated_difference',
    'total_updated_percentage',

    'default_interest_system',
    'default_interest_difference',
    'default_interest_percentage',

    'advocative_hours_system',
    'advocative_hours_difference',
    'advocative_hours_percentage',

    'total_due_creditor',
    'total_due_system',
    'total_due_difference',
    'total_due_percentage',

    'verbas',
    'verbas_integratorias',

]


class AbstractCalculationAdmin(admin.ModelAdmin):
    """
    Provides Readonly fields to Admin view of Calculations, displays Fields from the model provided:
        - recurral_system: Returns Recurral's system from Model.
        - recurral_difference: Returns Recurral's difference from Model.
        - recurral_percentage: Returns Recurral's percentage from Model.
        - total_updated_system: Returns Total Updated Charges' system from Model.
        - total_updated_difference: Returns Total Updated Charges' difference from Model.
        - total_updated_percentage: Returns Total Updated Charges' percentage from Model.
        - default_interest_system: Returns Default Interest's system from Model.
        - default_interest_difference: Returns Default Interest's difference from Model.
        - default_interest_percentage: Returns Default Interest's percentage from Model.
        - advocative_hours_system: Returns Advocative Hours' system from Model.
        - advocative_hours_difference: Returns Advocative Hours' difference from Model.
        - advocative_hours_percentage: Returns Advocative Hours' percentage from Model.
        - total_due_creditor: Total amount due to creditor for this calculation
        - total_due_system: Returns Total Due Charges' system from Model.
        - total_due_difference: Returns Total Due Charges' difference from Model.
        - total_due_percentage: Returns Total Due Charges' percentage from Model.
        - verbas: Returns the list of all Verbas used in each comparative
        - verbas_integratorias: Returns the list of all Verbas Integratorias used in each comparative

    Args:
        admin.ModelAdmin: Django's Default ModelAdmin Class.
    """
    readonly_fields = readonly_fields

    @admin.display(description='Sistema depósito recursal liberado')
    def recurral_system(self, model):
        return f'{model.recurral.system}'

    @admin.display(description='Diferença depósito recursal liberado')
    def recurral_difference(self, model):
        return f'{model.recurral.difference}'

    @admin.display(description='Porcentagem depósito recursal liberado')
    def recurral_percentage(self, model):
        return f'{model.recurral.percentage}'

    @admin.display(description='Sistema total atualizado')
    def total_updated_system(self, model):
        return f'{model.total_updated.system}'

    @admin.display(description='Diferença total atualizado')
    def total_updated_difference(self, model):
        return f'{model.total_updated.difference}'

    @admin.display(description='Porcentagem total atualizado')
    def total_updated_percentage(self, model):
        return f'{model.total_updated.percentage}'

    @admin.display(description='Sistema juros moratorios')
    def default_interest_system(self, model):
        return f'{model.default_interest.system}'

    @admin.display(description='Diferença juros moratorios')
    def default_interest_difference(self, model):
        return f'{model.default_interest.difference}'

    @admin.display(description='Porcentagem juros moratorios')
    def default_interest_percentage(self, model):
        return f'{model.default_interest.percentage}'

    @admin.display(description='Sistema honorarios advocaticios')
    def advocative_hours_system(self, model):
        return f'{model.advocative_hours.system}'

    @admin.display(description='Diferença honrarios advocaticios')
    def advocative_hours_difference(self, model):
        return f'{model.advocative_hours.difference}'

    @admin.display(description='Porcentagem honorarios advocaticios')
    def advocative_hours_percentage(self, model):
        return f'{model.advocative_hours.percentage}'

    @admin.display(description='Sistema total devido')
    def total_due_system(self, model):
        return f'{model.total_due_system}'

    @admin.display(description='Creditor total devido')
    def total_due_creditor(self, model):
        return f'{model.total_due_creditor}'

    @admin.display(description='Diferença total devido')
    def total_due_difference(self, model):
        return f'{model.total_due_difference}'

    @admin.display(description='Porcentagem total devido')
    def total_due_percentage(self, model):
        return f'{model.total_due_percentage}'

    readonly_fields = readonly_fields


def get_verbas(comparatives, funds):
    """
    A helper method to generate hyperlinks for the admin site based on Comparative models.

    It generates a list of hyperlinks with each link going to a specific detail view in the admin site.
    The method is only used by the ApprovedCalculationAdmin's verbas and verbas_integratorias methods.

    Args:
    - comparatives (QuerySet): A queryset including instances of the Comparative model.
    - funds (str): A string indicating which fund type the comparative instances belong to.

    :return:
    - formatted_html (django.utils.safestring.SafeText): a string of HTML-formatted text representing
      embedded hyperlinks to each Comparative model in the given queryset.

    Raises:
    - No specific exceptions are raised. Exceptions will only be caught and ignored while generating the hyperlinks.
    """
    list_href = []
    for comparative in comparatives:
        try:
            domain = Site.objects.get_current().domain
            url = F'{domain}/admin/funds/{funds}/{comparative.total_funds.id}/change/'
            href_certificate = format_html('<a href="{0}" target="_blank">{1}</a>', url, comparative.total_funds.fund)
            list_href.append(href_certificate)
        except AttributeError as e:
            logging.error(e)
    return format_html("<br>".join(list_href))


class ApprovedCalculationAdmin(AbstractCalculationAdmin):  # Calculo homologado
    """
    A ModelAdmin class containing the definition of fields displayed in the
    admin interface for the ApprovedCalculation instance.
    """

    def verbas(self, model):
        """
        A helper function that returns the approved funds for each ComparativeFunds instance belonging
        to a particular ApprovedCalculation instance.

        It uses the get_verbas method to query hyperlink information and return it in an HTML-formatted
        string.

        Args:
        - model (ApprovedCalculation): An instance of the ApprovedCalculation model class.

        :return:
        - formatted_html (django.utils.safestring.SafeText): an HTML-formatted string representing links
          to each ComparativeFunds instance under this ApprovedCalculation instance.

        Raises:
        - No specific exceptions are raised. Exceptions will only be caught during the execution of
          get_verbas helper method.
        """
        comparatives = model.get_comparatives()
        return get_verbas(comparatives, 'totalvaluesfunds')

    def verbas_integratorias(self, model):
        """
        A helper function that returns the approved integration funds for each ComparativeFundsIntegrations
        instance belonging to a particular ApprovedCalculation instance.

        It uses the get_verbas method to query hyperlink information and return it in an HTML-formatted
        string.

        Args:
        - model (ApprovedCalculation): An instance of the ApprovedCalculation model class.

        :return:
        - formatted_html (django.utils.safestring.SafeText): an HTML-formatted string representing links
          to each ComparativeFundsIntegrations instance under this ApprovedCalculation instance.

        Raises:
        - No specific exceptions are raised. Exceptions will only be caught during the execution of
          get_verbas helper method.
        """
        comparatives = model.get_comparatives_integrations()
        return get_verbas(comparatives, 'totalvaluesfundsintegrations')


admin.site.register(ComparativeCalculation, ComparativeCalculationAdmin)
admin.site.register(Comparative, ComparativeAdmin)
admin.site.register(ComparativeFunds, ComparativeFundsAdmin)
admin.site.register(ComparativeFundsIntegrations,
                    ComparativeFundsIntegrationsAdmin)
admin.site.register(ApprovedCalculation, ApprovedCalculationAdmin)
# admin.site.register(UpdatedCalculation, UpdatedCalculationAdmin)
