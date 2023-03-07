"""
Registers the Funds, StatementIntegrations, StatementFunds, StatementIRRF, MonetaryCorrection, MonetaryCorrectionIntegrations, TotalValuesIRRF and TotalValuesFunds models with the Django admin site.

This file facilitates the registration of the Funds, StatementIntegrations, StatementFunds, StatementIRRF, MonetaryCorrection, MonetaryCorrectionIntegrations, TotalValuesIRRF and TotalValuesFunds models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the funds.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Funds)
"""

from django.contrib import admin
from calculation.funds.models import Days, Interest, Fine, AmountDue, Funds, StatementIntegrations, StatementFunds, StatementIRRF, StatementDocuments, MonetaryCorrection, MonetaryCorrectionIntegrations, MonetaryCorrectionDocuments, TotalValuesIRRF, TotalValuesFunds, TotalValuesFundsIntegrations, ArrearsCharges


admin.site.register(Days)
admin.site.register(Interest)
admin.site.register(Fine)
admin.site.register(AmountDue)
admin.site.register(Funds)
admin.site.register(StatementFunds)
admin.site.register(StatementIntegrations)
admin.site.register(StatementIRRF)
admin.site.register(StatementDocuments)
admin.site.register(MonetaryCorrection)
admin.site.register(MonetaryCorrectionIntegrations)
admin.site.register(MonetaryCorrectionDocuments)
admin.site.register(TotalValuesIRRF)
admin.site.register(TotalValuesFunds)
admin.site.register(TotalValuesFundsIntegrations)
admin.site.register(ArrearsCharges)
