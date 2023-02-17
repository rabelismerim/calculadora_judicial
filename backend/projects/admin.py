"""
Registers the Project models with the Django admin site.

This file facilitates the registration of the Project models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the projects.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Project)
"""

from django.contrib import admin
from projects.models import Project


admin.site.register(Project)
