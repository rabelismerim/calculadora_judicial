from django.apps import AppConfig

from utils import _


class ClaimConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base.claim'
    verbose_name = _('Claim')
