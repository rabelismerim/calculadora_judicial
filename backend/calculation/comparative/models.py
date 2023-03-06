"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver
from base.models import AbstractDescription
from calculation.funds.models import TotalValuesFunds, TotalValuesFundsIntegrations
from calculation.models import Calculation
from core.abstract.models import AbstractModel


class Comparative(AbstractModel):
    """This class represents a Comparative model which is an AbstractModel."""
    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)

    # TODO: Esse valor pode ser nulo?
    data_base_creditor = models.DateField('Data base Credor')  # C4
    data_base_dtt = models.DateField('Data base DTT')  # D4

    @property
    def difference_date(self) -> int:  # E4 = D4 - C4
        """ Returns the difference between the Dates in days. """
        if not self.data_base_dtt or not self.data_base_creditor:
            return 0
        return int((self.data_base_dtt - self.data_base_creditor).days)

    def get_data_base_dtt(self):
        """ Returns the date of the creditor's recovering request from the DTT."""
        return self.calculation.creditor.recovering.project.date_rj_request

    def save(self, *args, **kwargs):
        """
        Save the instance of ComparativeFunds and calculate its dtt value
        Calculates the value of dtt using the get_dtt_value() method.
        """
        self.data_base_dtt = self.get_data_base_dtt()
        super(Comparative, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.calculation}'


class AbstractComparative(AbstractModel):
    creditor = models.FloatField(
        'Total creditor', default=0)  # C
    dtt = models.FloatField(
        'Total da DTT', default=0, editable=False)  # D

    @property
    def difference(self) -> float:  # E = C + D
        """Returns float: The difference between dtt and creditor."""
        return self.dtt - self.creditor

    @property
    def percentage(self) -> float:  # F = (D / C) -1
        """Returns float: The percentage difference between dtt and creditor. """
        try:
            return (((self.dtt or 0) / (self.creditor or 0)) - 1) * 100
        except ZeroDivisionError:
            return 0

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.creditor}'


class RecurralComparative(AbstractComparative):
    pass


class TotalUpdatedComparative(AbstractComparative):
    pass


class DefaultInterestComparative(AbstractComparative):
    pass


class AdvocativeHoursComparative(AbstractComparative):
    pass


class AbstractCalculation(AbstractDescription):  # Calculo homologado
    """
    This class represents a ComparativeCalculation object. 
    It has an associated OneToOneField connected to the 
    Comparative object and two DateFields for storing the data base 
    information of the creditor and DTT.

    Attributes:
        comparative (OneToOneField): Comparative model object with its own primary key
        total_creditor (FloatField): Total creditor amount
        total_dtt (FloatField): Total DTT amount
    """

    comparative = models.OneToOneField(Comparative, on_delete=models.PROTECT)

    recurral = models.OneToOneField(
        RecurralComparative, on_delete=models.PROTECT, null=True)  # V
    total_updated = models.OneToOneField(
        TotalUpdatedComparative, on_delete=models.PROTECT, null=True)  # V
    default_interest = models.OneToOneField(
        DefaultInterestComparative, on_delete=models.PROTECT, null=True)  # V
    advocative_hours = models.OneToOneField(
        AdvocativeHoursComparative, on_delete=models.PROTECT, null=True)  # V

    @property
    def total_due_creditor(self) -> float:  # C12 = C10 + C11 V
        """ Returns the difference between the Dates in days. """
        return self.total_updated.creditor + self.default_interest.creditor + self.get_total_advocative_hours_creditor()

    @property
    def total_due_dtt(self) -> float:  # D12 = D10 + D11 V
        """ Returns the difference between the Dates in days. """
        return self.total_updated.dtt + self.default_interest.dtt + self.get_total_advocative_hours_dtt()

    @property
    def total_due_difference(self) -> float:  # E12 = C12 + D12 V
        """Returns float: The difference between total_due_dtt and total_due_credor."""
        return self.total_due_dtt - self.total_due_creditor

    @property
    def total_due_percentage(self) -> float:  # F12 =  (D12 / C12) -1 V
        """Returns float: The percentage difference between total_due_dtt and total_due_creditor. """
        try:
            return (((self.total_due_dtt or 0) / (self.total_due_creditor or 0)) - 1) * 100
        except ZeroDivisionError:
            return 0

    def get_total_advocative_hours_dtt(self) -> float:
        """ Returns the recurral deposit of the statement"""
        if hasattr(self, 'advocative_hours'):
            return self.advocative_hours.dtt
        return 0

    def get_total_advocative_hours_creditor(self) -> float:
        """ Returns the recurral deposit of the statement"""
        if hasattr(self, 'advocative_hours'):
            return self.advocative_hours.creditor
        return 0

    def get_recurral_deposit_dtt(self) -> float:
        """ Returns the recurral deposit of the statement"""
        return self.comparative.calculation.statement.statementpf.recurraldeposit.value

    def get_default_interest_dtt(self) -> float:
        """ Returns the default interest of the statement"""
        return self.comparative.calculation.statement.statementpf.defaultinterest.value

    def get_advocative_hours_dtt(self) -> float:
        """ Returns the default interest of the statement"""
        return self.comparative.calculation.statement.get_total_lawyer()

    def __str__(self):
        return f'{self.comparative}'

    def save(self, *args, **kwargs):
        """
        Save the instance of ComparativeFunds and calculate its dtt value
        Calculates the value of dtt using the get_dtt_value() method.
        """
        self.recurral.dtt = self.get_recurral_deposit_dtt()
        self.recurral.save()
        self.default_interest.dtt = self.get_default_interest_dtt()
        self.default_interest.save()
        self.advocative_hours.dtt = self.get_advocative_hours_dtt()
        self.advocative_hours.save()
        super(AbstractCalculation, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class ApprovedCalculation(AbstractCalculation):  # Calculo atualizado
    """
    This class is used to store a OneToOne relationship with the Comparative model.
    """

    def get_comparatives(self):
        """ Returns all associated ComparativeFund objects."""
        return self.comparativefunds_set.all()


class UpdatedCalculation(AbstractCalculation):  # Calculo atualizado
    """
    This class is used to store a OneToOne relationship with the Comparative model.
    """

    def get_comparatives(self):
        """ Returns all associated ComparativeFundIntegrations objects."""
        return self.comparativefundsintegrations_set.all()


class AbstractComparativeFunds(AbstractDescription):
    """(AbstractDescription): Class for comparing funds with approved calculations."""
    value_claim_creditor = models.FloatField('Pedido do creditor')
    value_dtt = models.FloatField('Calculo da DTT')

    def save(self, *args, **kwargs):
        """
        Save the instance of AbstractComparativeFunds and calculate its dtt value
        Calculates the value of dtt using the get_dtt_value() method.
        """
        self.value_dtt = self.get_dtt_value()
        super(AbstractComparativeFunds, self).save(*args, **kwargs)

    def get_dtt_value(self):
        """Returns the total corrected value from TotalValuesFunds object."""
        return self.total_funds.total_corrected

    @property
    def difference(self):
        """Returns the difference between DTT calculated value and claim creditor value"""
        return (self.value_dtt or 0) - (self.value_claim_creditor or 0)

    @property
    def percentage(self):
        """Returns the percentage of difference between DTT calculated value and claim creditor value"""
        try:
            return (((self.value_dtt or 0) / (self.value_claim_creditor or 0)) - 1) * 100
        except ZeroDivisionError:
            return 0

    def __str__(self):
        return f'{self.value_claim_creditor}'

    class Meta:
        abstract = True


class ComparativeFunds(AbstractComparativeFunds):  # Calculo atualizado
    """
    This class is used to store a OneToOne relationship with the Comparative model.
    """
    approved_calculation = models.ForeignKey(
        ApprovedCalculation, on_delete=models.PROTECT)
    total_funds = models.OneToOneField(
        TotalValuesFunds, on_delete=models.PROTECT)


# Calculo atualizado
class ComparativeFundsIntegrations(AbstractComparativeFunds):
    """
    This class is used to store a OneToOne relationship with the Comparative model.
    """
    updated_calculation = models.ForeignKey(
        UpdatedCalculation, on_delete=models.PROTECT)
    total_funds = models.OneToOneField(
        TotalValuesFundsIntegrations, on_delete=models.PROTECT)


@receiver(post_save, sender=ComparativeFunds)
def update_comparative_total(sender, instance, **kwargs) -> None:
    """
    Updates the totals of the Comparative fields in an instance's approved Calculation.

    Iterates through each Comparative of the ComparativeFunds instance and adds the respective values to 
    one or more variables based on their value type before saving the calculation with the updated values.

    Parameters:
        sender    (Class)   : The class that triggered the post_save signal.
        instance  (Object)  : The instance that is being saved.
        **kwargs  (dict)    : Keyword arguments passed as part of the post_save signal.

    Returns:
        None
    """
    comparatives = instance.approved_calculation.get_comparatives()
    sum_total_updated_dtt = instance.approved_calculation.recurral.dtt
    sum_total_updated_creditor = instance.approved_calculation.recurral.creditor
    calculation = instance.approved_calculation
    for comparative in comparatives:
        sum_total_updated_dtt += comparative.value_dtt
        sum_total_updated_creditor += comparative.value_claim_creditor
    calculation.total_updated.dtt = sum_total_updated_dtt
    calculation.total_updated.creditor = sum_total_updated_creditor
    calculation.total_updated.save()


@receiver(post_save, sender=ComparativeFundsIntegrations)
def update_comparative_integrations_total(sender, instance, **kwargs) -> None:
    """
    Updates the totals of the Comparative fields in an instance's approved Calculation.

    Iterates through each Comparative of the ComparativeFunds instance and adds the respective values to 
    one or more variables based on their value type before saving the calculation with the updated values.

    Parameters:
        sender    (Class)   : The class that triggered the post_save signal.
        instance  (Object)  : The instance that is being saved.
        **kwargs  (dict)    : Keyword arguments passed as part of the post_save signal.

    Returns:
        None
    """
    comparatives = instance.updated_calculation.get_comparatives()
    sum_total_updated_dtt = instance.updated_calculation.recurral.dtt
    sum_total_updated_creditor = instance.updated_calculation.recurral.creditor
    calculation = instance.updated_calculation
    for comparative in comparatives:
        sum_total_updated_dtt += comparative.value_dtt
        sum_total_updated_creditor += comparative.value_claim_creditor
    calculation.total_updated.dtt = sum_total_updated_dtt
    calculation.total_updated.creditor = sum_total_updated_creditor
    calculation.total_updated.save()
