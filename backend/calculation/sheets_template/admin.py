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

def load_files(modeladmin, request, queryset):
    for obj in queryset:
        rows = obj.get_excel_to_json()

        if len(rows) == 0:
            continue

        cont = 0
        if len(rows) > 0:
            messages.success(
                request, f'Carregado template do arquivo {obj.filename}')
        else:
            messages.warning(
                request, f'Nenhum indice carregado do arquivo {obj.filename}')

admin.site.register(SheetsTemplate)
