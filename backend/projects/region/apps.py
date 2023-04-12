from django.apps import AppConfig

from utils import _


class RegionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects.region'
    verbose_name = _("Region")
