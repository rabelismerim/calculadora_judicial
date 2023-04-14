from django.apps import AppConfig

from utils import _


class VerdictConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculation.verdict'
    verbose_name = _('Verdict')
