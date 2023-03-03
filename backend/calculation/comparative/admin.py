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


admin.site.register(Comparative)
admin.site.register(ComparativeFundsIntegrations)


class ComparativeFundsAdmin(admin.ModelAdmin):
    readonly_fields = ('value_dtt', 'difference', 'percentage')


readonly_fields = ('data_base_dtt',
                   'difference_date',

                   'recurral_deposit_dtt',
                   'difference_recurral_deposit',
                   'percentage_recurral_deposit',

                   'total_updated_creditor',
                   'total_updated_dtt',
                   'difference_total_updated',
                   'percentage_total_updated',

                   'default_interest_dtt',
                   'difference_default_interest',
                   'percentage_default_interest',

                   'total_due_creditor',
                   'total_due_dtt',
                   'difference_total_due',
                   'percentage_total_due',

                   )


class ApprovedCalculationAdmin(admin.ModelAdmin):
    readonly_fields = readonly_fields


class UpdatedCalculationAdmin(admin.ModelAdmin):
    readonly_fields = readonly_fields


admin.site.register(ComparativeFunds, ComparativeFundsAdmin)
admin.site.register(ApprovedCalculation, ApprovedCalculationAdmin)
admin.site.register(UpdatedCalculation, UpdatedCalculationAdmin)
