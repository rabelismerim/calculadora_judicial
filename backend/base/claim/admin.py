"""
Registers the ClaimCreditor, ClaimLawyer, and Claim models with the Django admin site.

This file facilitates the registration of the ClaimCreditor, ClaimLawyer, and Claim models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the base.claim.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(ClaimCreditor)
"""


from django.contrib import admin
from base.claim.models import ClaimCreditor, ClaimLawyer, Claim

admin.site.register(ClaimCreditor)
admin.site.register(ClaimLawyer)
admin.site.register(Claim)
