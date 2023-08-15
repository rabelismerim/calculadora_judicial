"""
Registers the Creditor models with the Django admin site.

This file facilitates the registration of the Creditor models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the creditors.creditor.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Creditor)
"""
from django import forms
from django.contrib import admin
from creditors.models import Creditor, LegalPendencies


class CreditorForm(forms.ModelForm):
    class Meta:
        model = Creditor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rate'].queryset = self.fields['rate'].queryset.filter(is_active=True)


class CreditorModelAdmin(admin.ModelAdmin):
    list_display = ('total', 'total_historical')
    form = CreditorForm


admin.site.register(LegalPendencies)
admin.site.register(Creditor, CreditorModelAdmin)
