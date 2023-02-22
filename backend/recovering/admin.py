"""
Registers the Recovering models with the Django admin site.

This file facilitates the registration of the Recovering models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the recovering.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django Recovering's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Recovering)
"""

from django.contrib import admin
from recovering.models import Recovering


admin.site.register(Recovering)
