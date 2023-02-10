from django.db import models
from core.abstract.models import AbstractModel


class Coins(AbstractModel):

    COIN_CHOICES = (
        ("B", "BRL"),
        ("E", "EUR"),
        ("U", "US$"),
        ("C", "CAN$")
    )
    coin = models.CharField(
        max_length=1, verbose_name='Descrição', choices=COIN_CHOICES, default='B')
    value = models.FloatField(default=0)

    def __str__(self):
        return f"{self.get_coin_display()}"
