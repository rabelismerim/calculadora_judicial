"""
Registers the Premise models with the Django admin site.

This file facilitates the registration of the Premise models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the premise.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Premise)
"""

from django.contrib import admin
from calculation.premise.models import Premise


admin.site.register(Premise)
