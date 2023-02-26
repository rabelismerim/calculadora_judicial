"""
Registers the ArchiveRecovering models with the Django admin site.

This file facilitates the registration of the ArchiveRecovering models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the recovering.archive_recovering.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django ArchiveRecovering's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(ArchiveRecovering)
"""

from django.contrib import admin
from recovering.archive_recovering.models import ArchiveRecovering


admin.site.register(ArchiveRecovering)
