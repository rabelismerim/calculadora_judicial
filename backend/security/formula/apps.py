from django.apps import AppConfig

from utils import _


class FormulaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'security.formula'
    verbose_name = _('Formula')
