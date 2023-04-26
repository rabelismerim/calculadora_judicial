"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from base.views import ExtractFormula
from calculation.comparative.signals import gen_statement_integrations
from calculation.funds.abstract.models import AbstractStatement, AbstractMonetaryCorrection, \
    AbstractTotalValuesFunds
from rates.models import Rate


class StatementIntegrations(AbstractStatement):
    """
    A model class representing a financial statement for a fund.

    This class inherits from the AbstractStatement class and extends it to represent a financial statement
    for a fund. It includes attributes such as a 'database date', historical value, and a foreign key relationship
    to a 'Funds' object.

    In the Excel sheet, Statement Funds refers to each piece of data that can be inserted in the table of funds
    database in the budget sheets, including tst, moral damages, etc.

    Attributes:
        Same as in the AbstractStatement class.

    Methods:
        - has_monetary_correction(self) -> bool: Returns True if the monetary correction exists for the statement.
        - _set_status(self, value: str): Sets the status of the statement with the given value.
        - calcule_monetary_correction(self): Calculates the monetary correction for the statement if it exists.
        - get_corrected_value(self) -> float: Retrieves the corrected value of the statement if the monetary correction
          exists, or else returns 0.

    Note:
        The 'calcule_monetary_correction()' method uses the '_get_index_monetary_correction()' method, which should be
        defined in the class that inherits or implements the 'AbstractStatement' class.
    """
    description = models.CharField(_('Description fund'), max_length=150)
    summary = models.BooleanField(_('Apply summary 381?'), default=False)

    class Meta:
        verbose_name = 'Statement Fund Integration'
        verbose_name_plural = 'Statement Funds Integrations'

    def has_monetary_correction(self) -> bool:
        """Returns True if the monetary correction exists for the statement."""
        return hasattr(self, 'monetarycorrectionintegrations')

    def get_monetary_correction(self):
        """Returns the `monetarycorrection` attribute value"""
        if self.has_monetary_correction():
            return self.monetarycorrectionintegrations

    def calcule_monetary_correction(self):
        """Retrieves the corrected value of the statement if the monetary correction exists, or else returns 0."""
        data = self._get_index_monetary_correction()
        if data:
            MonetaryCorrectionIntegrations.objects.update_or_create(defaults=data, **{'statement': self})
            self.set_calculation_done()

    def get_corrected_value(self) -> float:
        """Returns corrected value if the monetary correction exists for the statement, else 0"""
        if self.has_monetary_correction():
            return self.monetarycorrectionintegrations.corrected_value
        return 0

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the StatementIntegrations object and send a post-save signal.
        Args:
            send_signal_post_save (bool): Set to True to send a post-save signal. Default is True.
        """
        super(StatementIntegrations, self).save(*args, **kwargs)
        if send_signal_post_save:
            gen_statement_integrations.send(sender=self.__class__, instance=self)


class MonetaryCorrectionIntegrations(AbstractMonetaryCorrection):
    """
    A class that represents a monetary correction for a statement of integrations.

    In <Excel>, it refers to each piece of data that can be inserted in the table of integral funds,
    monetary correction in the sum sheets (tst, moral damages, etc.)

    Attributes:
        statement (StatementIntegrations): The statement of integrations to which the monetary correction applies.
    """
    statement = models.OneToOneField(
        StatementIntegrations, on_delete=models.PROTECT)


class TotalValuesFundsIntegrations(AbstractTotalValuesFunds):
    """
    A class that represents the total values of a fund, which is a concrete implementation of AbstractTotalValuesFunds.

    Attributes:
        total_historical (float): The historical value of the fund.
        total_corrected (float): The corrected value of the fund.
        fund (Funds): The fund to which the values apply.

    Methods:
        get_calculated_statement(): Returns the calculated statement of the fund.
        set_total(): Calculates and sets the total corrected and historical values of the fund based on the calculated statement.
    """
    fund = models.OneToOneField('funds.Funds', on_delete=models.PROTECT)

    def get_calculated_statement(self):
        """Returns the calculated statement of the fund."""
        return self.fund.statementintegrations_set.filter(status='C')

    def set_total(self):
        """
        Calculates and sets the total corrected and historical values of the fund based on the calculated
        statement.
        """
        statements = self.get_calculated_statement()
        total_corrected_value = 0
        total_historical_value = 0
        for statement in statements:
            total_corrected_value += statement.get_corrected_value()
            total_historical_value += statement.get_total_value()
        self.total_historical = total_corrected_value
        self.total_corrected = total_historical_value
        self.save()

    class Meta:
        verbose_name = 'Total value fund integration'
        verbose_name_plural = 'Total values funds integrations'


@receiver(gen_statement_integrations, sender=StatementIntegrations)
def save_rate_integrations(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementIntegrations object is saved. It
    calculates the monetary correction for the instance and generates the total integrations of the related fund. It
    takes the sender and instance as arguments.

    Triggers the creation of the formulas used at the end of the calculation
    """
    print('Signal gerar linha extrato verbas integratorias\n')
    instance.calcule_monetary_correction()
    instance.fund.gen_total_integrations()

    statement_methods = ['get_total_value', 'get_dsr_reflexes', 'get_monetary_correction',
                         'calcule_monetary_correction', 'get_rate_by_date',
                         '_get_index_monetary_correction', 'get_corrected_value', 'get_data_base', 'get_total_value',
                         'get_historical_value', 'get_rate', 'save_total_funds', 'monetarycorrection', 'set_total',
                         '_calc_corrected_value', 'has_monetary_correction', '_calc_corrected_value', 'corrected_value']

    ExtractFormula(instance, instance.fund.calculation, statement_methods).get_methods(
        [StatementIntegrations, MonetaryCorrectionIntegrations, Rate, TotalValuesFundsIntegrations,
         save_rate_integrations])
