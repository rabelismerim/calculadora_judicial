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

    def __str__(self):
        return f'{self.calculation}'


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
    # TODO: Esse valor pode ser nulo?
    data_base_creditor = models.DateField('Data base Credor')  # C4
    data_base_dtt = models.DateField('Data base DTT')  # D4

    @property
    def difference_date(self) -> int:  # E4 = D4 - C4
        """ Returns the difference between the Dates in days. """
        if not self.data_base_dtt or not self.data_base_creditor:
            return 0
        return int((self.data_base_dtt - self.data_base_creditor).days)

    recurral_deposit_creditor = models.FloatField(
        'Deposito recursal liberado do creditor', default=0)  # C9
    recurral_deposit_dtt = models.FloatField(
        'Deposito recursal liberado da DTT', default=0)  # D9

    @property
    def difference_recurral_deposit(self) -> float:  # E9 = C9 + D9 V
        """Returns float: The difference between recurral_deposit_dtt and recurral_deposit_creditor."""
        return self.recurral_deposit_dtt - self.recurral_deposit_creditor

    @property
    def percentage_recurral_deposit(self) -> float:  # F9 = (D9 / C9) -1 V
        """Returns float: The percentage difference between recurral_deposit_dtt and recurral_deposit_creditor. """
        try:
            return (self.recurral_deposit_dtt / self.recurral_deposit_creditor) - 1
        except ZeroDivisionError:
            return 0

    total_updated_creditor = models.FloatField(
        'Total atualizado do creditor', default=0)  # C10
    total_updated_dtt = models.FloatField(
        'Total atualizado da DTT', default=0)  # D10

    @property
    def difference_total_updated(self) -> float:  # E10 = C10 + D10 V
        """Returns float: The difference between total_updated_dtt and total_updated_creditor."""
        return self.total_updated_dtt - self.total_updated_creditor

    @property
    def percentage_total_updated(self) -> float:  # F10 = (D10 / C10) -1 V
        """Returns float: The percentage difference between total_updated_dtt and total_updated_creditor. """
        try:
            return (self.total_updated_dtt / self.total_updated_creditor) - 1
        except ZeroDivisionError:
            return 0

    default_interest_creditor = models.FloatField(
        'Juros moratórios Creditor', default=0)  # C11
    default_interest_dtt = models.FloatField(
        'Juros moratórios DTT', default=0)  # D11

    @property
    def difference_default_interest(self) -> float:  # E11 = C11 + D11 V
        """Returns float: The difference between default_interest_dtt and default_interest_creditor."""
        return self.default_interest_dtt - self.default_interest_creditor

    @property
    def percentage_default_interest(self) -> float:  # F11 = (D11 / C11) -1 V
        """Returns float: The percentage difference between default_interest_dtt and default_interest_creditor. """
        try:
            return (self.default_interest_dtt / self.default_interest_creditor) - 1
        except ZeroDivisionError:
            return 0

    @property
    def total_due_creditor(self) -> float:  # C12 = C10 + C11 V
        """ Returns the difference between the Dates in days. """
        return self.total_updated_creditor + self.default_interest_creditor

    @property
    def total_due_dtt(self) -> float:  # D12 = D10 + D11 V
        """ Returns the difference between the Dates in days. """
        return self.total_updated_dtt + self.default_interest_dtt

    @property
    def difference_total_due(self) -> float:  # E12 = C12 + D12 V
        """Returns float: The difference between total_due_dtt and total_due_credor."""
        return self.total_due_dtt - self.total_due_creditor

    @property
    def percentage_total_due(self) -> float:  # F12 =  (D12 / C12) -1 V
        """Returns float: The percentage difference between total_due_dtt and total_due_creditor. """
        try:
            return (self.total_due_dtt / self.total_due_creditor) - 1
        except ZeroDivisionError:
            return 0

    def get_data_base_dtt(self):
        """ Returns the date of the creditor's recovering request from the DTT."""
        return self.comparative.calculation.creditor.recovering.date_rj_request

    def get_default_interest_dtt(self) -> float:
        """ Returns the default interest of the statement"""
        return self.comparative.calculation.statement.statementpf.defaultinterest.value

    def get_recurral_deposit_dtt(self) -> float:
        """ Returns the recurral deposit of the statement"""
        return self.comparative.calculation.statement.statementpf.recurraldeposit.value

    def __str__(self):
        return f'{self.comparative}'

    def save(self, *args, **kwargs):
        """
        Save the instance of ComparativeFunds and calculate its dtt value
        Calculates the value of dtt using the get_dtt_value() method.
        """
        self.data_base_dtt = self.get_data_base_dtt()
        self.default_interest_dtt = self.get_default_interest_dtt()
        self.recurral_deposit_dtt = self.get_recurral_deposit_dtt()
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
        return self.value_dtt - self.value_claim_creditor

    @property
    def percentage(self):
        """Returns the percentage of difference between DTT calculated value and claim creditor value"""
        return (self.value_dtt / self.value_claim_creditor) - 1

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
    sum_total_updated_dtt = 0
    sum_total_updated_creditor = 0
    calculation = instance.approved_calculation
    for comparative in comparatives:
        sum_total_updated_dtt += comparative.value_dtt
        sum_total_updated_creditor += comparative.value_claim_creditor
    calculation.total_updated_dtt = sum_total_updated_dtt
    calculation.total_updated_creditor = sum_total_updated_creditor
    calculation.save()


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
    sum_total_updated_dtt = 0
    sum_total_updated_creditor = 0
    calculation = instance.updated_calculation
    for comparative in comparatives:
        sum_total_updated_dtt += comparative.value_dtt
        sum_total_updated_creditor += comparative.value_claim_creditor
    calculation.total_updated_dtt = sum_total_updated_dtt
    calculation.total_updated_creditor = sum_total_updated_creditor
    calculation.save()
