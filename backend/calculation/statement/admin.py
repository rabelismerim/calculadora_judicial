"""
Registers the Statement models with the Django admin site.

This file facilitates the registration of the Statement models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the calculation.statement.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Statement)
"""

from django.contrib import admin
from calculation.statement.models import Statement, TotalLawyer, Lawyer


admin.site.register(Statement)
admin.site.register(TotalLawyer)
admin.site.register(Lawyer)
