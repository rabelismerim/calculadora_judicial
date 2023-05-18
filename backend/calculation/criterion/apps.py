from django.apps import AppConfig

from utils import _


class CriterionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculation.criterion'
    verbose_name = _('Criterion')
