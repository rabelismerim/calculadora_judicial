from django.apps import AppConfig

from utils import _


class AbstractConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.abstract'
    verbose_name = _("Abstract User")

