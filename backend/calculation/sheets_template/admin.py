"""
Registers the Template Sheet models with the Django admin site.

This file generate any sheet used by consumption by frontend.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(TypeCalculation)
"""

from django.contrib import admin

from calculation.sheets_template.models import SheetsTemplate

admin.site.register(SheetsTemplate)
