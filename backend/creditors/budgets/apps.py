from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BudgetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'creditors.budgets'
    verbose_name = _("Verbas")