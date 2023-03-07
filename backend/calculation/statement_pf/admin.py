"""
Registers the StatementPF models with the Django admin site.

This file facilitates the registration of the StatementPF models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the statement_pf.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(StatementPF)
"""

from django.contrib import admin

from calculation.statement_pf.models import StatementPF, TaxDays, RecurralDeposit, DefaultInterest, DefaultInterestDue, TotalDue, FundsDescription

admin.site.register(StatementPF)
admin.site.register(TaxDays)
admin.site.register(RecurralDeposit)
admin.site.register(DefaultInterest)
admin.site.register(DefaultInterestDue)
admin.site.register(TotalDue)
admin.site.register(FundsDescription)
