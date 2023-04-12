from django.apps import AppConfig

from utils import _


class RatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rates'
    verbose_name = _("Rates")
