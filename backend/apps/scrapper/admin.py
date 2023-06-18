"""
Registers the Scrapper models with the Django admin site.

This file facilitates the registration of the Scrapper models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the scrapper.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Scrapper)
"""
from django.contrib import admin
from apps.scrapper.models import Scrapper


admin.site.register(Scrapper)
