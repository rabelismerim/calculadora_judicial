"""
This module defines a Django AppConfig class for configuring the 'premise' app.

The PremiseConfig class inherits from the AppConfig class and sets the default_auto_field
attribute to 'django.db.models.BigAutoField' to use a Big Integer field as the primary key
for all models by default. The name attribute is set to 'premise', which is the name of the app
this configuration belongs to.

Attributes:
- default_auto_field: A string representing the default primary key field type for all models
- name: A string representing the name of the app
"""
# import vinaigrette
from django.apps import AppConfig

from utils import _


class PremiseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculation.premise'
    verbose_name = _('Premise')
    verbose_plural_name = _('Premise')

    def ready(self):
        Premise = self.get_model("Premise")
        # vinaigrette.register(Premise, ['description'])
