from django.apps import AppConfig

from utils import _


class SheetTemplateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calculation.sheets_template'
    verbose_name = _('Sheets Template')
