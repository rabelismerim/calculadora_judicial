from django.apps import AppConfig

from utils import _


class EntityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.entity'
    verbose_name = _("Entidade")

