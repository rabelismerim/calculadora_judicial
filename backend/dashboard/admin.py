"""
Registers the Dashboard models with the Django admin site.

This file facilitates the registration of the Dashboard models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the recovering.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django Dashboard's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Dashboard)
"""

from django.contrib import admin

from dashboard.models import Dashboard, LoginRecord

admin.site.register(Dashboard)
admin.site.register(LoginRecord)
