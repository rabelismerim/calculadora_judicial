from django.apps import AppConfig

from utils import _


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.users'
    verbose_name = _("User")
