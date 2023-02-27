from django.db import models

from core.abstract.models import AbstractModel
from creditors.models import Creditor


class Calculation(AbstractModel):
    creditor = models.ForeignKey(Creditor, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.creditor}'
