from django.db import models
from calculation.models import Calculation
from core.abstract.models import AbstractModel
from utils import _


class TypeCalculation(AbstractModel):
    # Danos materiais, Morais, Outros
    description = models.CharField(_('Description'), max_length=255)
    calculation = models.CharField(_('Calculation'), max_length=255)


class Verdict(AbstractModel):
    """Sentença adicional"""
    description = models.CharField(_('Description'), max_length=50)
    value = models.FloatField(_('Value'))
    type_calculation = models.ForeignKey(TypeCalculation, on_delete=models.PROTECT)
    calculation = models.ForeignKey(Calculation, on_delete=models.PROTECT)
