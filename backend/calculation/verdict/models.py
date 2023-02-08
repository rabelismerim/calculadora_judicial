from django.db import models
from calculation.models import Calculation
from core.abstract.models import AbstractModel


class TypeCalculation(AbstractModel):
    description = models.CharField('Descrição', max_length=255)
    calculation = models.CharField('Cálculo', max_length=255)


class Verdict(AbstractModel):
    description = models.CharField('Descrição', max_length=50)
    value = models.FloatField('Valor')
    type_calculation = models.ForeignKey(
        TypeCalculation, on_delete=models.PROTECT)
    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)
