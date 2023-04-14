"""
This module defines a Django AppConfig class for configuring the 'statement_pf' app.

The StatementPFConfig class inherits from the AppConfig class and sets the default_auto_field
attribute to 'django.db.models.BigAutoField' to use a Big Integer field as the primary key
for all models by default. The name attribute is set to 'statement_pf', which is the name of the app
this configuration belongs to.

Attributes:
- default_auto_field: A string representing the default primary key field type for all models
- name: A string representing the name of the app
"""


from django.apps import AppConfig

from django.utils.translation import gettext_lazy as _


class StatementPFConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculation.statement_pf'
    verbose_name = _('Statement PF')
