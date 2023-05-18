from django.db import models

from core.abstract.models import AbstractModel
from utils import _

CLASSE_CHOICES = (
    ('1', _('Classe I - Working')),
    ('2', _('Classe II - Real Guarantee')),
    ('3', _('Classe III - Unsecured')),
    ('4', _('Classe IV - ME/EPP')),
)


class Classes(AbstractModel):
    classe = models.CharField(_('Class'), max_length=1, default='1', choices=CLASSE_CHOICES)

    def __str__(self):
        return str(self.get_classe_display())
