"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models
from calculation.models import Calculation
from core.abstract.models import AbstractModel

CHOICES_TOTAL = (
    ('A', 'Total atualizado'),
    ('D', 'Total devido')
)

CHOICES_TAX_DAYS = (
    ('T', 'Taxa SELIC no período'),
    ('D', 'Dias em atraso')
)

CHOICES_DEFAULT_INTEREST_DUE = (
    ('T', 'Total após juros de mora'),
    ('D', 'Total devido')
)


class Total(AbstractModel):
    field_description = models.CharField(
        'Legenda', max_length=1, choices=CHOICES_TOTAL)
    value = models.FloatField('Valor', max_length=150)


class TaxDays(AbstractModel):
    field_description = models.CharField(
        'Legenda', max_length=1, choices=CHOICES_TOTAL)
    value = models.FloatField('Valor', max_length=150)


class DefaultInterestDue(AbstractModel):
    field_description = models.CharField(
        'Legenda', max_length=1, choices=CHOICES_DEFAULT_INTEREST_DUE)
    value = models.FloatField('Valor', max_length=150)


class DefaultInterestDue(AbstractModel):
    bankruptcy_credit = models.CharField(
        'Crédito inteiramente concursal? ', max_length=1, choices=CHOICES_DEFAULT_INTEREST_DUE)
    value = models.FloatField('Valor', max_length=150)


class Statement(AbstractModel):
    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)
    # TODO: definir operações de lógica para as legendas e calculo

    default_interest = models.FloatField('Juros moratórios',
                                         null=True)  # Juros moratórios ou EXCLUIR LINHA

    recurral_deposit_released = models.FloatField(
        'Depósito recursal liberado', null=True)  # Depósito recursal liberado ou EXCLUIR LINHA

    # Total atualizado ou Total devido
    total = models.OneToOneField(Total, on_delete=models.PROTECT)

    tax_days = models.OneToOneField(
        TaxDays, on_delete=models.PROTECT, null=True)  # Taxa SELIC no período, dias em atraso ou EXCLUIR LINHA

    default_interest_due = models.OneToOneField(
        DefaultInterestDue, on_delete=models.PROTECT, null=True)  # Total após juros de mora, Total devido ou EXCLUIR LINHA

    def __str__(self):
        return f'{self.calculation}'
