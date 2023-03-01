"""
Registers the StatementPJ models with the Django admin site.

This file facilitates the registration of the StatementPJ models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the statement_pf.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(StatementPJ)
"""

from django.contrib import admin

from calculation.statement_pj.models import StatementPJ, FundsDescriptionPJ

admin.site.register(StatementPJ)
admin.site.register(FundsDescriptionPJ)
