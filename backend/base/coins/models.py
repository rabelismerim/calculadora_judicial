from django.db import models
from django.utils.translation import gettext_lazy as _
from core.abstract.models import AbstractModel

COIN_CHOICES = (
    ("B", "BRL"),
    ("E", "EUR"),
    ("U", "US$"),
    ("C", "CAN$")
)


class Coins(AbstractModel):
    coin = models.CharField(max_length=1, verbose_name=_('Moeda'), choices=COIN_CHOICES, default='B')
    value = models.FloatField(default=0)

    def __str__(self):
        return f"{self.get_coin_display()}"
