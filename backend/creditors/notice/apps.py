from django.apps import AppConfig

from utils import _


class NoticeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'creditors.notice'
    verbose_name = _("Notice")
