from django.apps import AppConfig

from utils import _


class RecoveringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base.coins'
    verbose_name = _("Coins")
