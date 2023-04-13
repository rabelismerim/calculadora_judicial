from django.apps import AppConfig

from utils import _


class PermissionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.permission'
    verbose_name = _("Permission")

