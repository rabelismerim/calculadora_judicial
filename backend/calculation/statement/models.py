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
    """
    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)
    conclusion = models.CharField('Legenda da conclusão', max_length=1, choices=CHOICES_CONCLUSION, default='I')

    def get_statement_pf(self):
        if hasattr(self, 'statementpf'):
            return self.statementpf

    def get_total_lawyer(self):
        if hasattr(self, 'totallawyer'):
            return self.totallawyer.value
        return 0

    def get_recurral_deposit(self):
        statement_pf = self.get_statement_pf()
        if statement_pf:
            return statement_pf.get_recurral_deposit()
        return 0

    def get_default_interest(self):
        statement_pf = self.get_statement_pf()
        if statement_pf:
            return statement_pf.get_default_interest()
        return 0

    @property
    def total_conclusion(self) -> float or None:
        # TODO: verify statement pj
        statement_pf = self.get_statement_pf()
        if statement_pf:
            return statement_pf.total_conclusion

    def __str__(self):
        return f'{self.calculation}'


class TotalLawyer(AbstractModel):
    """
    Represents the total value of a group of lawyers' fees for a Statement.

    Attributes:
        total (float): The total value of the lawyers' fees.
        statement (Statement): The statement that this total belongs to.
    """
    total = models.FloatField('Valor')
    statement = models.OneToOneField(Statement, on_delete=models.PROTECT)

    def _get_lawyers(self):
        return self.lawyer_set.all()

    def calcule_total(self):
        self.save()

    def save(self, *args, **kwargs):
        lawyers = self._get_lawyers()
        self.total = sum([x.total_calculated for x in lawyers if x.total_calculated])
        super().save(*args, **kwargs)


class Lawyer(AbstractModel):
    """
    Represents a single lawyer's fee for a Statement.

    Attributes:
        name (str): The name of the lawyer.
        total (float): The value of the lawyer's fee.
        total_lawyer (TotalLawyer): The total value that this fee contributes to.
    """
    name = models.CharField('Nome do advogado', max_length=150)
    total = models.FloatField('Valor')
    total_lawyer = models.ForeignKey(TotalLawyer, on_delete=models.PROTECT)

    def _get_advocative_hours(self) -> float:
        return self.total_lawyer.statement.calculation.criterion.advocative_hours

    @property
    def total_calculated(self) -> float or None:
        advocative_hours = self._get_advocative_hours()
        if advocative_hours > 0:
            """=IF(N7="Sim";C40;IF($B$19<$B$18;IFERROR(C38;C36);IF($B$19>=$B$18;IFERROR($C$40;$C$35))))*B23"""
            total_conclusion = self.total_lawyer.statement.total_conclusion
            if total_conclusion:
                return total_conclusion * advocative_hours / 100

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.total_lawyer.calcule_total()
