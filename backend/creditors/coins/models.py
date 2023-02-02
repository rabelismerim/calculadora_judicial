from django.db import models
from core.abstract.models import AbstractModel


class Coins(AbstractModel):

    DESCRIPTION_CHOICES = (
        ("B","BRL"),
        ("E","EUR"),
        ("U","US$"),
        ("C","CAN$")
    )        
    description = models.CharField(max_length=1, verbose_name='Descrição', choices=DESCRIPTION_CHOICES, default='B')

    def __str__(self):
        return f"{self.get_description_display()}"
    