"""
Registers the BigNumber models with the Django admin site.

This file facilitates the registration of the BigNumber models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the big_number.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(BigNumber)
"""
from django.contrib import admin
from big_number.models import BigNumber, BigNumberMethod, BigNumberMethodFields

admin.site.register(BigNumber)
admin.site.register(BigNumberMethod)
admin.site.register(BigNumberMethodFields)
