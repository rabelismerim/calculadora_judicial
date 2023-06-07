"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models
from calculation.models import Calculation
from core.abstract.models import AbstractModel
from utils import _

CHOICES_CONCLUSION = (('I', _('Impugnment')), ('H', _('Qualification')))


class Statement(AbstractModel):
    """
    Represents a statement with a conclusion and optional edital.

    Attributes:
        calculation (Calculation): The calculation that this statement belongs to.
        conclusion (str): A one-character string indicating the conclusion of the statement.
    """
    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)
    conclusion = models.CharField(_('Conclusion legend'), max_length=1, choices=CHOICES_CONCLUSION, default='I')

    def get_statement_pf(self):
        """
        Gets the statementpf attribute of the object if it exists.

        Returns:
            - The statementpf attribute of the object, if it exists.
            - None, otherwise.
        """
        if hasattr(self, 'statementpf'):
            return self.statementpf

    def get_statement_pj(self):
        """
        Gets the statementpj attribute of the object if it exists.

        Returns:
            - The statementpj attribute of the object, if it exists.
            - None, otherwise.
        """
        if hasattr(self, 'statementpj'):
            return self.statementpj

    def get_total_lawyer(self) -> float:
        """
        Gets the value of the totallawyer attribute of the object if it exists.

        Returns:
            - The value of the totallawyer attribute of the object, if it exists.
            - 0, otherwise.
        """
        if hasattr(self, 'totallawyer'):
            return self.totallawyer.value
        return 0

    def get_recurral_deposit(self) -> float:
        """
        Calls the get_recurral_deposit method of the object's statementpf attribute if it exists.

        Returns:
            - The result of calling the get_recurral_deposit method of the object's statementpf attribute, if it exists.
            - 0, otherwise.
        """
        statement_pf = self.get_statement_pf()
        if statement_pf:
            return statement_pf.get_recurral_deposit()
        return 0

    def get_default_interest(self) -> float:
        statement_pf = self.get_statement_pf()
        if statement_pf:
            return statement_pf.get_default_interest()
        return 0

    @property
    def total_conclusion(self) -> float:
        """
        Get the total value of the conclusion, corrected and calculated with fines and interest
        """
        statement_pf = self.get_statement_pf()
        statement_pj = self.get_statement_pj()
        if statement_pf:
            return statement_pf.total_conclusion
        elif statement_pj:
            return statement_pj.corrected_value
        return 0

    @property
    def total_corrected(self) -> float:
        """
        Get the corrected total value, just applying the index
        """
        statement_pf = self.get_statement_pf()
        statement_pj = self.get_statement_pj()
        if statement_pf:
            return statement_pf.total
        elif statement_pj:
            return statement_pj.corrected_value
        return 0

    def __str__(self):
        return f'{self.calculation}'


class TotalLawyer(AbstractModel):
    """
    Represents the total value of a group of lawyers' fees for a Statement.

    Attributes:
        total (float): The total value of the lawyers' fees.
        statement (Statement): The statement that this total belongs to.
    """
    total = models.FloatField(_('Total'))
    statement = models.OneToOneField(Statement, on_delete=models.PROTECT)

    def _get_lawyers(self):
        """
        Returns a queryset of all the lawyers associated with this instance.
        """
        return self.lawyer_set.all()

    def calcule_total(self):
        """
        Calculates the total cost of all lawyers associated with this instance, and saves the instance.
        """
        self.save()

    def save(self, *args, **kwargs):
        """
        Overrides the save method to calculate the total cost of all lawyers associated with this instance,
        and then saves the instance. Also includes optional arguments *args and **kwargs that can be passed
        to the parent class's save method.
        """
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
    name = models.CharField(_('Lawyer name'), max_length=150)
    total = models.FloatField(_('Total'))
    total_lawyer = models.ForeignKey(TotalLawyer, on_delete=models.PROTECT)

    def _get_advocative_hours(self) -> float:
        """
        Return the number of advocative hours calculated based on the lawyer's total statement and calculation criterion.
        """
        return self.total_lawyer.statement.calculation.criterion.advocative_hours

    @property
    def total_calculated(self) -> float or None:
        """
        Return the total calculated value based on the lawyer's total statement and calculation criterion,
        considering the advocative hours if they are greater than 0. The calculation follows a specific formula,
        which includes the total conclusion and advocative hours percentage.
        """
        advocative_hours = self._get_advocative_hours()
        if advocative_hours > 0:
            """=IF(N7="Sim";C40;IF($B$19<$B$18;IFERROR(C38;C36);IF($B$19>=$B$18;IFERROR($C$40;$C$35))))*B23"""
            total_conclusion = self.total_lawyer.statement.total_conclusion
            if total_conclusion:
                return total_conclusion * advocative_hours / 100

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.total_lawyer.calcule_total()
