from django.apps import AppConfig

from utils import _


class CalculationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculation'
    verbose_name = _("Calculation")
