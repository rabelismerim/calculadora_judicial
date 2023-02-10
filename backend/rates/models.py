from django.db import models

from core.abstract.models import AbstractModel


class Rate(AbstractModel):  # Edital
    # TODO: estruturar indices
    INDEX_CHOICES = (
        ('T', 'TST'),
        ('E', 'TST-E'),
    )
    index = models.CharField(
        'Tipo de indice', max_length=1, choices=INDEX_CHOICES)

    def __str__(self):
        return f"{self.get_index_display()}"
