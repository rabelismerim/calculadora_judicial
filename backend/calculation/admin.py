"""
Registers the Calculation models with the Django admin site.

This file facilitates the registration of the Calculation models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the calculation.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Calculation)
"""
from django.contrib import admin
from calculation.models import Calculation, Incident

admin.site.register(Incident)


class CalculationModelAdmin(admin.ModelAdmin):
    readonly_fields = ('premises', 'approver', 'special_approvers', 'executor', 'reviewer', 'get_classes', 'get_total_funds')


admin.site.register(Calculation, CalculationModelAdmin)
