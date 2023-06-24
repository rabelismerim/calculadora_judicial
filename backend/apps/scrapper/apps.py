"""
This module defines a Django AppConfig class for configuring the 'scrapper' app.

The ScrapperConfig class inherits from the AppConfig class and sets the default_auto_field
attribute to 'django.db.models.BigAutoField' to use a Big Integer field as the primary key
for all models by default. The name attribute is set to 'scrapper', which is the name of the app
this configuration belongs to.

Attributes:
- default_auto_field: A string representing the default primary key field type for all models
- name: A string representing the name of the app
"""
from django.apps import AppConfig

from utils import _


class ScrapperConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.scrapper'
    verbose_name = _('Scrapper')
    verbose_plural_name = _('Scrappers')
