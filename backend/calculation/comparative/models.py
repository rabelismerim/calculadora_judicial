"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from base.models import AbstractDescription
from calculation.comparative.signals import gen_calc
from calculation.funds.integrations.models import TotalValuesFundsIntegrations
from calculation.funds.models import TotalValuesFunds
from calculation.models import Calculation
from core.abstract.models import AbstractModel
from django.db import models
from django.dispatch import receiver
from utils import _


class Comparative(AbstractModel):
    """
    A model that represents a comparative between the creditor's Claim value and the DTT calculation.

    Fields:
    - calculation (models.OneToOneField): The foreign key reference to a Calculation instance.
    - data_base_creditor (models.DateField): The Creditor base date of comparison.
    - data_base_dtt (models.DateField): The DTT base date of comparison.
    Methods:
    get_data_base_dtt(): Returns the date of the creditor's recovering request from the DTT.
    get_dates(): Returns a dictionary with the values for the dates related to this Comparative object.
    check_create_editable_total_funds(): Verifies if all funds related to the current Comparative object have comparable
    values in the TotalValuesFunds model.
    check_create_editable_total_funds_integrations(): Verifies if all funds related to the current Comparative object
    have comparable values in the TotalValuesFundsIntegrations model.
    get_create_approved_calculationations(): Creates and returns an instance of
    the ApprovedCalculation class related to the current Comparative object if such instance does not exist yet.
    """

    # def __init__(self, *args, **kwargs):
    #     super(Comparative, self).__init__(*args, **kwargs)

    #     if hasattr(self, 'calculation'):
    #         self.checks()

    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)

    # TODO: Esse valor pode ser nulo?
    data_base_creditor = models.DateField(
        _('Creditor base date'), null=True)  # C4
    data_base_dtt = models.DateField(_('DTT base date'), null=True)  # D4

    @property
    def difference_date(self) -> int:  # E4 = D4 - C4
        """ Returns the difference between the Dates in days. """
        if not self.data_base_dtt or not self.data_base_creditor:
            return 0
        return int((self.data_base_dtt - self.data_base_creditor).days)

    def get_data_base_dtt(self):
        """Returns the date of the creditor's recovering request from the DTT."""
        return self.calculation.creditor.recovering.project.date_rj_request

    def get_dates(self):
        """
        Returns a dictionary with the values for the dates related to this Comparative object, including:
            The creditor date
            The dtt (Department of Taxation and Finance) date
            The difference between the two dates.
        """
        return {
            'creditor': self.data_base_creditor,
            'dtt': self.data_base_dtt,
            'difference': self.difference_date,
        }

    def checks(self) -> bool:
        """
        Verifies if all funds related to the current Comparative object have comparable values in the
        TotalValuesFunds model. If not found, creates a new ComparativeFunds object for each missing fund with
        creditor equal zero. Returns a boolean indicating wheter any funds were missing.
        """
        self.check_create_editable_total_funds()
        self.check_create_editable_total_funds_integrations()

    def check_create_editable_total_funds(self) -> bool:
        """
        Verifies if all funds related to the current Comparative object have comparable values in the
        TotalValuesFunds model. If not found, creates a new ComparativeFunds object for each missing fund with
        creditor equal zero. Returns a boolean indicating wheter any funds were missing.
        """
        funds = TotalValuesFunds.objects.filter(
            fund__calculation=self.calculation, comparativefunds__isnull=True)
        for fund in funds:
            ComparativeFunds.objects.get_or_create(
                total_funds=fund, calculation=self.get_create_approved_calculation(), creditor=0)
        return bool(funds)

    def check_create_editable_total_funds_integrations(self) -> bool:
        """
        Verifies if all integration funds related to the current Comparative object have comparable values in the
        TotalValuesFundsIntegrations model. If not found, creates a new ComparativeFundsIntegrations object for each
        missing fund with creditor equal zero.
        Returns a boolean indicating wheter any funds were missing.
        """
        funds = TotalValuesFundsIntegrations.objects.filter(
            fund__calculation=self.calculation, comparativefundsintegrations__isnull=True)
        for fund in funds:
            ComparativeFundsIntegrations.objects.get_or_create(
                total_funds=fund, calculation=self.get_create_approved_calculation(), creditor=0)
        return bool(funds)

    def get_create_approved_calculation(self):
        """
        Creates and returns an instance of the ApprovedCalculation class related to the current Comparative object if
        such instance does not exist yet.
        """
        if hasattr(self, 'approvedcalculation') is False:
            approved = ApprovedCalculation.objects.filter(
                comparative=self).first()
            if not approved:
                approved = ApprovedCalculation.objects.create(
                    comparative=self,
                    recurral=ComparativeCalculation.objects.create(),
                    total_updated=ComparativeCalculation.objects.create(),
                    default_interest=ComparativeCalculation.objects.create(),
                    advocative_hours=ComparativeCalculation.objects.create(),
                )
            return approved
        return self.approvedcalculation

    def save(self, *args, **kwargs):
        """
        Save the instance of ComparativeFunds and calculate its dtt value
        Calculates the value of dtt using the get_dtt_value() method.
        """
        self.data_base_dtt = self.get_data_base_dtt()
        super(Comparative, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.calculation}'


class ComparativeCalculation(AbstractDescription):
    """
    This is an abstract model class that serves as a base for other comparative models in the application. 
    Fields:
    - creditor (models.FloatField): The amount requested by the creditor.
    - dtt (models.FloatField): The value calculated by dtt, generated in other operations.

    Properties:
    - difference (Float): The difference between dtt and creditor.
    - percentage (Float): The percentage difference between dtt and creditor.
    """
    creditor = models.FloatField(_("Creditor's total"), default=0)  # C
    dtt = models.FloatField(_('DTT total'), default=0)  # D

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

    def __str__(self):
        return f'{self.creditor}'


class ApprovedCalculation(AbstractDescription):  # Calculo homologado
    """
    Attributes:
    comparative: A OneToOneField to a Comparative object, protected from deletion.
    recurral: A OneToOneField to a RecurralComparative object, protected from deletion, can be null.
    total_updated: A OneToOneField to a TotalUpdatedComparative object, protected from deletion, can be null.
    default_interest: A OneToOneField to a DefaultInterestComparative object, protected from deletion, can be null.
    advocative_hours: A OneToOneField to a AdvocativeHoursComparative object, protected from deletion, can be null.

    Properties:
    total_due_creditor: Computes the value of total due creditor by adding up the values of the creditor attribute of
     total_updated, default_interest, and advocative_hours objects.
    total_due_dtt: Computes the value of total due DTT by adding up the values of the dtt attribute of total_updated,
    default_interest, and advocative_hours objects.
    total_due_difference: Returns the difference between the values of total_due_dtt and total_due_creditor.
    total_due_percentage: Returns the percentage difference between total_due_dtt and total_due_creditor.

    Methods:
    get_total_advocative_hours_dtt(): Returns the value of the dtt attribute of advocative_hours, or 0 if
     advocative_hours is None.
    get_total_advocative_hours_creditor(): Returns the value of the creditor attribute of advocative_hours, or 0 if
     advocative_hours is None.
    get_recurral_deposit_dtt(): Returns the value of the recurral deposit as computed by the get_recurral_deposit()
     method of a statement of a calculation associated with the comparative attribute of this object.
    get_default_interest_dtt(): Returns the value of the default interest as computed by the get_default_interest()
     method of a statement of a calculation associated with the comparative attribute of this object.
    get_advocative_hours_dtt(): Returns the total number of lawyer hours as computed by the get_total_lawyer() method
     of a statement of a calculation associated with the comparative attribute of this object.
    get_comparatives(): Returns all associated ComparativeFund objects.
    get_comparatives_integrations(): Returns all associated ComparativeFundIntegrations objects.
    generate_calculations(): Generates calculations for the instance of ApprovedCalculation and saves it. This includes
     updating the attribute recurral, adding up all funds and integration funds, and updating attributes total_updated,
      default_interest, and advocative_hours."""
    comparative = models.OneToOneField(Comparative, on_delete=models.PROTECT)

    recurral = models.OneToOneField(
        ComparativeCalculation, on_delete=models.PROTECT, related_name='calc_recurral')  # V
    total_updated = models.OneToOneField(
        ComparativeCalculation, on_delete=models.PROTECT, related_name='calc_total_updated')  # V
    default_interest = models.OneToOneField(
        ComparativeCalculation, on_delete=models.PROTECT, related_name='calc_default_interest')  # V
    advocative_hours = models.OneToOneField(
        ComparativeCalculation, on_delete=models.PROTECT, related_name='calc_advocative_hours')  # V

    @property
    def total_due_creditor(self) -> float:  # C12 = C10 + C11 V
        """Returns the total dues owed to the creditor. 

        :return:
            float: Total dues owed to creditor, including value claim, default interest, and advocative hours.
        """
        return self.total_updated.creditor + self.default_interest.creditor + self.get_total_advocative_hours_creditor()

    @property
    def total_due_dtt(self) -> float:  # D12 = D10 + D11 V
        """Returns the total dues owed to DTT.

        :return:
            float: Total dues owed to DTT, including value claim, default interest, and advocative hours.
        """
        return self.total_updated.dtt + self.default_interest.dtt + self.get_total_advocative_hours_dtt()

    @property
    def total_due_difference(self) -> float:  # E12 = C12 + D12 V
        """Returns the difference between the total amount owed to the creditor and the total amount owed to DTT.

        :return:
            float: The difference between the total amount owed to the creditor and the total amount owed to DTT.
        """
        return self.total_due_dtt - self.total_due_creditor

    @property
    def total_due_percentage(self) -> float:  # F12 =  (D12 / C12) -1 V
        """Returns float: The percentage difference between total_due_dtt and total_due_creditor."""
        try:
            return (((self.total_due_dtt or 0) / (self.total_due_creditor or 0)) - 1) * 100
        except ZeroDivisionError:
            return 0

    def get_total_due(self):
        return {
            'creditor': self.total_due_creditor,
            'dtt': self.total_due_dtt,
            'difference': self.total_due_difference,
            'percentage': self.total_due_percentage,
        }

    def get_total_advocative_hours_dtt(self) -> float:
        """Returns float: The dtt value of AdvocativeHoursComparative if it exists, otherwise returns 0."""
        if hasattr(self, 'advocative_hours'):
            return self.advocative_hours.dtt
        return 0

    def get_total_advocative_hours_creditor(self) -> float:
        """Returns float: The creditor value of AdvocativeHoursComparative if it exists, otherwise returns 0."""
        if hasattr(self, 'advocative_hours'):
            return self.advocative_hours.creditor
        return 0

    def get_recurral_deposit_dtt(self) -> float:
        """Returns float: The recurral deposit value from the associated CalculationStatement object."""

        try:
            return self.comparative.calculation.statement.get_recurral_deposit()
        except:
            return 0

    def get_default_interest_dtt(self) -> float:
        """Returns float: The default interest value from the associated CalculationStatement object."""
        return self.comparative.calculation.statement.get_default_interest_value()

    def get_advocative_hours_dtt(self) -> float:
        """Returns float: The total credited advocative hours value from the associated CalculationStatement object."""
        try:
            return self.comparative.calculation.statement.get_total_lawyer()
        except:
            return 0

    def __str__(self):
        return f'{self.comparative}'

    def save(self, *args, **kwargs):
        """
        Overrides the parent class' save function to generate calculations and save it.
        Triggered when an approved calculation object is saved.
        """
        self.generate_calculations()
        super(ApprovedCalculation, self).save(*args, **kwargs)

    def get_comparatives(self):
        """ 
        Returns all associated ComparativeFund objects related to this approved calculation.

        :return:
            list | QuerySet: List of comparative fund objects generated from given query.
        """
        return self.comparativefunds_set.all()

    def get_comparatives_integrations(self):
        """ 
        Returns all associated ComparativeFundIntegrations objects related to this approved calculation.

        :return:
            list | QuerySet: List of comparative fund integration objects generated from given query.
        """
        return self.comparativefundsintegrations_set.all()

    def generate_calculations(self):
        """
        Generates a set of calculations based on stored data for this object.
        """
        # Update recurral deposit
        self.recurral.dtt = self.get_recurral_deposit_dtt()
        self.recurral.save()

        # Start from the recurral deposit
        sum_total_updated_dtt = self.recurral.dtt
        sum_total_updated_creditor = self.recurral.creditor

        # Add up all funds
        comparatives = self.get_comparatives()
        for comparative in comparatives:
            sum_total_updated_dtt += comparative.get_dtt_value()
            sum_total_updated_creditor += comparative.creditor

        # Add up all integration funds
        comparatives = self.get_comparatives_integrations()
        for comparative in comparatives:
            sum_total_updated_dtt += comparative.get_dtt_value()
            sum_total_updated_creditor += comparative.creditor

        # Save in total updated
        calculation = self.total_updated
        calculation.dtt = sum_total_updated_dtt
        calculation.creditor = sum_total_updated_creditor
        calculation.save()

        # Update default interests
        self.default_interest.dtt = self.get_default_interest_dtt()
        self.default_interest.save()

        # Update advocative hours
        self.advocative_hours.dtt = self.get_advocative_hours_dtt()
        self.advocative_hours.save()


# class UpdatedCalculation(AbstractCalculation):  # Calculo atualizado
#     """
#     This class is used to store a OneToOne relationship with the Comparative model.
#     """

#     def get_comparatives(self):
#         """ Returns all associated ComparativeFundIntegrations objects."""
#         return self.comparativefundsintegrations_set.all()


class AbstractComparativeFunds(AbstractDescription):
    """(AbstractDescription): Class for comparing funds with approved calculations."""
    creditor = models.FloatField(_("Creditor's request"))
    dtt = models.FloatField(_('DTT calculation'))
    calculation = models.ForeignKey(
        ApprovedCalculation, on_delete=models.PROTECT)
    total_funds = None

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the instance of AbstractComparativeFunds and calculate its dtt value
        Calculates the value of dtt using the get_dtt_value() method.
        """
        self.dtt = self.get_dtt_value()
        super(AbstractComparativeFunds, self).save(*args, **kwargs)
        if send_signal_post_save:
            gen_calc.send(sender=self.__class__, instance=self)

    def get_dtt_value(self) -> float:
        """Returns the total corrected value from TotalValuesFunds object."""
        return self.get_total_funds().total_corrected

    def get_total_funds(self):
        if hasattr(self, 'total_funds') is False:
            raise NotImplementedError(
                _('Must have the total_funds relation to inherit this method'))
        return self.total_funds

    @property
    def name(self):
        return self.get_total_funds().fund.name

    @property
    def difference(self) -> float:
        """Returns the difference between DTT calculated value and claim creditor value"""
        return (self.dtt or 0) - (self.creditor or 0)

    @property
    def percentage(self) -> float:
        """Returns the percentage of difference between DTT calculated value and claim creditor value"""
        try:
            return (((self.dtt or 0) / (self.creditor or 0)) - 1) * 100
        except ZeroDivisionError:
            return 0

    def __str__(self):
        return f'{self.name}'

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')


class ComparativeFunds(AbstractComparativeFunds):  # Calculo atualizado
    """
    This class is used to store a OneToOne relationship with the Comparative model.
    """
    total_funds = models.OneToOneField(
        TotalValuesFunds, on_delete=models.PROTECT)


class ComparativeFundsIntegrations(AbstractComparativeFunds):
    """
    This class is used to store a OneToOne relationship with the Comparative model.
    """
    total_funds = models.OneToOneField(
        TotalValuesFundsIntegrations, on_delete=models.PROTECT)


@receiver(gen_calc, sender=ComparativeFunds)
def update_comparative_total(sender, instance, **kwargs) -> None:
    """
    Signal function that updates the total calculations in the associated ApprovedCalculation whenever a ComparativeFunds
    instance is saved.

    :param sender: The model class that sent the signal.
    :type sender: django.db.models.Model
    :param instance: The instance of ComparativeFunds that was just saved.
    :type instance: myapp.models.ComparativeFunds
    :param kwargs: Additional keyword arguments passed by the signal.
    :type kwargs: dict
    :return: None
    """
    instance.calculation.generate_calculations()


@receiver(gen_calc, sender=ComparativeFundsIntegrations)
def update_comparative_integrations_total(sender, instance, **kwargs) -> None:
    """
    Signal function that updates the total calculations in the associated ApprovedCalculation whenever a
    ComparativeFundsIntegrations instance is saved.

    :param sender: The model class that sent the signal.
    :type sender: django.db.models.Model
    :param instance: The instance of ComparativeFundsIntegrations that was just saved.
    :type instance: myapp.models.ComparativeFundsIntegrations
    :param kwargs: Additional keyword arguments passed by the signal.
    :type kwargs: dict
    :return: None
    """
    instance.calculation.generate_calculations()
