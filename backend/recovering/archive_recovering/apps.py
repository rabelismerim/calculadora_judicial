from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArchiveRecoveringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recovering.archive_recovering'
    verbose_name = _("Arquivo Recuperanda")
