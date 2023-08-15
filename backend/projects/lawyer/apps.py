from django.apps import AppConfig

from utils import _


class LawyerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects.lawyer'
    verbose_name = _("Lawyer")
