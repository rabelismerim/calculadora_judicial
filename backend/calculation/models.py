from django.db import models

from core.abstract.models import AbstractModel
from creditors.models import Creditor

CHOICES_STEP = (('S', 'Solicitado'), ('E', 'Em revisão'), ('C', 'Calculado'),
                ('A', 'Aprovado'), ('R', 'Reprovado'))


class Calculation(AbstractModel):
    creditor = models.ForeignKey(Creditor, on_delete=models.PROTECT)
    step = models.CharField(
        'Passo do cálculo', max_length=1, choices=CHOICES_STEP, default='S')
    appeal_credit = models.BooleanField(
        'Crédito inteiramente concursal?', default=False)
    appeal_deposit = models.BooleanField(
        'Levantamento de depósito recursal?', default=False)
    has_advocative_hours = models.BooleanField(
        'Há honorários no cálculo homologado?', default=False)
    credit_authorization_date = models.DateField(
        'Data da certidão de habilitação de crédito', null=True, default=None)

    # TODO: definir como @property?
    # True If edital AJ else False
    has_edital = models.BooleanField(
        'Edital art. 7º § 2 - 11.101/2005', default=False)

    def __str__(self):
        return f'{self.creditor}'
