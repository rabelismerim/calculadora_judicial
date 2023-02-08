from django.db import models

from core.abstract.models import AbstractModel


class Classes(AbstractModel):
    CLASSE_CHOICES = (
        ('1', 'Classe I - Trabalhista'),
        ('2', 'Classe II - Garantia Real'),
        ('3', 'Classe III - Quirografário'),
        ('4', 'Classe IV - ME/EPP'),
    )
    classe = models.CharField('Classe', max_length=1,
                              default='1', choices=CLASSE_CHOICES)
