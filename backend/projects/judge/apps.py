from django.apps import AppConfig

from utils import _


class JudgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects.judge'
    verbose_name = _("Judge")
