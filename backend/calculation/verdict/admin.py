"""
Registers the TypeCalculation and Verdict models with the Django admin site.

This file facilitates the registration of the TypeCalculation and Verdict models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the calculation.verdict.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(TypeCalculation)
"""

from django.contrib import admin

from calculation.verdict.models import TypeCalculation, Verdict

admin.site.register(TypeCalculation)
admin.site.register(Verdict)
