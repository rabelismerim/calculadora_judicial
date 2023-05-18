from django.apps import AppConfig

from utils import _


class CourtConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects.court'
    verbose_name = _("Court")
