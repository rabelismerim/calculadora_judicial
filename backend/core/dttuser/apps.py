from django.apps import AppConfig

from utils import _


class DTTUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.dttuser'
    verbose_name = _("DTTUser")
