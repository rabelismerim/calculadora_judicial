"""
Registers the File models with the Django admin site.

This file facilitates the registration of the File models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the file.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(File)
"""
from django.contrib import admin
from file.models import File, GenericModelPath


admin.site.register(File)
admin.site.register(GenericModelPath)
