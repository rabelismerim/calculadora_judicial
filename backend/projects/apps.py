from django.apps import AppConfig

from utils import _


class ProjetoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects'
    verbose_name = _('Project')
