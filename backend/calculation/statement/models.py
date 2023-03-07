"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models
from calculation.models import Calculation
from core.abstract.models import AbstractModel


CHOICES_CONCLUSION = (('I', 'Impugnação'), ('H', 'Habilitação'))


class Statement(AbstractModel):
    """
    Represents a statement with a conclusion and optional edital.

    Attributes:
        calculation (Calculation): The calculation that this statement belongs to.
        conclusion (str): A one-character string indicating the conclusion of the statement.
        has_edital (bool): Whether this statement has an edital.
    """
    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)
    # TODO: definir operações de lógica para as legendas e calculo

    conclusion = models.CharField(
        'Legenda da conclusão', max_length=1, choices=CHOICES_CONCLUSION)

    def get_total_lawyer(self):
        if hasattr(self, 'totallawyer'):
            return self.totallawyer.value
        return 0

    def get_recurral_deposit(self):
        if hasattr(self, 'statementpf'):
            return self.statementpf.get_recurral_deposit()
        return 0

    def get_default_interest(self):
        if hasattr(self, 'statementpf'):
            return self.statementpf.get_default_interest()
        return 0

    def __str__(self):
        return f'{self.calculation}'


# TODO: Tabela estatica. Criar no evento signals.post.save ou em Procedure
class TotalLawyer(AbstractModel):
    """
    Represents the total value of a group of lawyers' fees for a Statement.

    Attributes:
        value (float): The total value of the lawyers' fees.
        total_pf (Statement): The statement that this total belongs to.
    """
    value = models.FloatField('Valor')
    statement = models.OneToOneField(Statement, on_delete=models.PROTECT)


# TODO: Tabela estatica. Criar no evento signals.post.save ou em Procedure
class Lawyer(AbstractModel):
    """
    Represents a single lawyer's fee for a Statement.

    Attributes:
        name (str): The name of the lawyer.
        valor (float): The value of the lawyer's fee.
        total_lawyer (TotalLawyer): The total value that this fee contributes to.
    """
    name = models.CharField('Nome do advogado', max_length=150)
    valor = models.FloatField('Valor')
    total_lawyer = models.ForeignKey(TotalLawyer, on_delete=models.PROTECT)
