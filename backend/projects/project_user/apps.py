from django.apps import AppConfig

from utils import _


class ProjectUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projects.project_user'
    verbose_name = _("Project User")
