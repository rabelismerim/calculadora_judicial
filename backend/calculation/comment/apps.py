"""
This module defines a Django AppConfig class for configuring the 'comment' app.

The CommentConfig class inherits from the AppConfig class and sets the default_auto_field
attribute to 'django.db.models.BigAutoField' to use a Big Integer field as the primary key
for all models by default. The name attribute is set to 'comment', which is the name of the app
this configuration belongs to.

Attributes:
- default_auto_field: A string representing the default primary key field type for all models
- name: A string representing the name of the app
"""

from django.apps import AppConfig

from utils import _


class CommentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculation.comment'
    verbose_name = _('Comment')
    verbose_plural_name = _('Comments')
