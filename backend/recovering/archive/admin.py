"""
Registers the Archive models with the Django admin site.

This file facilitates the registration of the Archive models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the recovering.archive.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django Archive's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Archive)
"""

from django.contrib import admin
from recovering.archive.models import Archive


admin.site.register(Archive)
