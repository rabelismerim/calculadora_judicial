"""
This module defines a Django AppConfig class for configuring the 'big_number' app.

The BigNumberConfig class inherits from the AppConfig class and sets the default_auto_field
attribute to 'django.db.models.BigAutoField' to use a Big Integer field as the primary key
for all models by default. The name attribute is set to 'big_number', which is the name of the app
this configuration belongs to.

Attributes:
- default_auto_field: A string representing the default primary key field type for all models
- name: A string representing the name of the app
"""
from django.apps import AppConfig

from utils import _


class BigNumberConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'big_number'
    verbose_name = _('BigNumber')
    verbose_plural_name = _('BigNumbers')
