"""
Defines models for financial statements and funds.

AbstractModel is inherited for common fields such as id, created_at, and updated_at.
Funds class is used to represent a financial fund with a name and calculation.
AbstractStatement class is an abstract model used to represent a financial statement,
with fields for a Data base date, historical value, and a foreign key to Funds.
StatementFunds class extends AbstractStatement to represent a statement related to funds.
StatementIntegrations extends AbstractStatement and includes a description field.
"""
from django.db import models
from django.db.models import FloatField
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from calculation.comparative.signals import gen_statement_funds, gen_total_funds
from calculation.funds.abstract.models import AbstractFunds, AbstractStatement, AbstractMonetaryCorrection, \
    AbstractTotalValuesFunds
from calculation.funds.integrations.models import TotalValuesFundsIntegrations


class Funds(AbstractFunds):
    """
    This class defines methods for generating total statements and fetching the TotalValuesFunds and
    TotalValuesFundsIntegrations objects associated with a fund. These objects store the total values and
    integrations for the fund respectively.

    Methods:
        get_total_funds(): Returns the TotalValuesFunds object associated with the current fund object. If the
                           object does not exist, it creates one and returns it.

        get_total_integrations(): Rerturns the TotalValuesFundsIntegrations object associated with the current
                                 fund object. If the object does not exist, it creates one and returns it.

        gen_total_statements(): Generates total statements for the current fund by calling the set_total() method
                                of the TotalValuesFunds object associated with it.

        gen_total_integrations(): Generates total statements for the current fund by calling the set_total() method
                                  of the TotalValuesFundsIntegrations object associated with it.
    """

    class Meta:
        verbose_name = 'Fund'
        verbose_name_plural = 'Funds'

    def get_total_funds(self):
        """
        This method returns the TotalValuesFunds object associated with the current fund object. If the object does
        not exist, it creates one and returns it.
        """
        if hasattr(self, 'totalvaluesfunds'):
            return self.totalvaluesfunds
        return TotalValuesFunds.objects.get_or_create(fund=self)[0]

    def get_total_integrations(self):
        """
        This method returns the TotalValuesFundsIntegrations object associated with the current fund object. If the
        object does not exist, it creates one and returns it.
        """
        if hasattr(self, 'totalvaluesfundsintegrations'):
            return self.totalvaluesfundsintegrations
        return TotalValuesFundsIntegrations.objects.get_or_create(fund=self)[0]

    def gen_total_statements(self):
        """
        This method generates the total statements for the current fund by calling the set_total() method of the
        TotalValuesFunds object associated with it.
        """
        total_funds = self.get_total_funds()
        total_funds.set_total()

    def gen_total_integrations(self):
        """
        This method generates the total statements for the current fund by calling the set_total() method of the
        TotalValuesFundsIntegrations object associated with it.
        """
        total_funds = self.get_total_integrations()
        total_funds.set_total()


class StatementFunds(AbstractStatement):
    """
    A model class representing a financial statement for a fund.

    This class inherits from the AbstractStatement class and extends it to represent a financial statement
    for a fund. It includes attributes such as a 'database date', historical value, and a foreign key relationship
    to a 'Funds' object.

    In the Excel sheet, Statement Funds refers to each piece of data that can be inserted in the table of funds
    database in the budget sheets, including tst, moral damages, etc.

    Attributes:
        Same as in the AbstractStatement class.
        dsr_reflexes (FloatField): The dsr reflexes for this statement.


    Methods:
        - has_monetary_correction(self) -> bool: Returns True if the monetary correction exists for the statement.
        - _set_status(self, value: str): Sets the status of the statement with the given value.
        - calcule_monetary_correction(self): Calculates the monetary correction for the statement if it exists.
        - get_corrected_value(self) -> float: Retrieves the corrected value of the statement if the monetary correction
          exists, or else returns 0.

    Note:
    The 'calcule_monetary_correction()' method uses the '_get_index_monetary_correction()' method, which should be defined
    in the class that inherits or implements the 'AbstractStatement' class.
    """
    dsr_reflexes = models.FloatField(_('DSR Reflexes'), default=0)  # DRS - Descanso semanal remunerado
    summary = models.BooleanField(_('Apply Precedent 381?'), default=False)

    class Meta:
        verbose_name = 'Statement Fund'
        verbose_name_plural = 'Statement Funds'

    def get_total_value(self) -> float:
        """Returns the total value of an asset by summing its historical value and the value of its DSR reflexes.

        Returns:
            float: The total value of the asset.
        """
        # TODO: check if template has option dsr_reflexes checked
        return self.historical_value + self.dsr_reflexes

    def get_dsr_reflexes(self) -> FloatField:
        """Returns the `dsr_reflexes` attribute value"""
        return self.dsr_reflexes

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the StatementFunds object and send a post-save signal.
        Args:
            send_signal_post_save (bool): Set to True to send a post-save signal. Default is True.
        """
        super(StatementFunds, self).save(*args, **kwargs)
        if send_signal_post_save:
            gen_statement_funds.send(sender=self.__class__, instance=self)

    def has_monetary_correction(self) -> bool:
        """Returns True if the monetary correction exists for the statement."""
        return hasattr(self, 'monetarycorrection')

    def get_monetary_correction(self):
        """Returns the `monetarycorrection` attribute value"""
        if self.has_monetary_correction():
            return self.monetarycorrection

    def calcule_monetary_correction(self):
        """Retrieves the corrected value of the statement if the monetary correction exists, or else returns 0."""
        data = self._get_index_monetary_correction()
        if data:
            MonetaryCorrection.objects.update_or_create(
                defaults=data, **{'statement': self})
            self.set_calculation_done()

    def get_corrected_value(self) -> float:
        """Returns corrected value if the monetary correction exists for the statement, else 0"""
        if self.has_monetary_correction():
            return self.monetarycorrection.corrected_value
        return 0


class MonetaryCorrection(AbstractMonetaryCorrection):
    """
    A class that represents a monetary correction for a statement of funds.

    In <Excel>, it refers to each piece of data that can be inserted in the table of funds, monetary correction in the
    rates sheets (tst, moral damages, etc.)

    Attributes:ø
        statement (StatementFunds): The statement of funds to which the monetary correction applies.
    """
    statement = models.OneToOneField(StatementFunds, on_delete=models.PROTECT)


class TotalValuesFunds(AbstractTotalValuesFunds):
    """
    A class that represents the total values of a fund, which is a concrete implementation of AbstractTotalValuesFunds.

    Attributes:
        total_historical (float): The historical value of the fund.
        total_corrected (float): The corrected value of the fund.
        total_dsr_reflexes (float): The drs reflexes value of the fund.
        total_accurate (float): The total accurate value of the fund.
        fund (Funds): The fund to which the values apply.

    Methods:
        get_calculated_statement(): Returns the calculated statement of the fund.
        set_total(): Calculates and sets the total corrected and historical values of the fund based on the calculated
         statement.
    """
    total_dsr_reflexes = models.FloatField(
        _('Total valor reflexos DSR'), default=0)
    total_accurate = models.FloatField(_('Total accurate'), default=0)
    fund = models.OneToOneField(Funds, on_delete=models.PROTECT)

    def get_calculated_statement(self):
        """Returns the calculated statement of the fund."""
        return self.fund.statementfunds_set.filter(status='C')

    def set_total(self):
        """
        Calculates and sets the total corrected and historical values of the fund based on the calculated
        statement.
        """
        statements = self.get_calculated_statement()

        total_corrected_value = 0
        total_historical_value = 0
        total_dsr_reflexes = 0
        total_accurate = 0

        for statement in statements:
            total_corrected_value += statement.get_corrected_value()
            total_historical_value += statement.get_historical_value()
            total_dsr_reflexes += statement.get_dsr_reflexes()
            total_accurate += statement.get_total_value()

        self.total_historical = total_historical_value
        self.total_corrected = total_corrected_value
        self.total_dsr_reflexes = total_dsr_reflexes
        self.total_accurate = total_accurate
        self.save()

    class Meta:
        verbose_name = 'Total values fund'
        verbose_name_plural = 'Total values funds'


@receiver(gen_statement_funds, sender=StatementFunds)
def save_rate(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementFunds object is saved. It
    calculates the monetary correction for the instance and generates the total statements of the related fund. It
    takes the sender and instance as arguments
    """
    print('Signal gerar linha extrato verbas\n')

    instance.calcule_monetary_correction()
    instance.fund.gen_total_statements()


@receiver(gen_total_funds, sender=Funds)
def save_total_funds(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementFunds object is saved. It
    calculates the monetary correction for the instance and generates the total statements of the related fund. It
    takes the sender and instance as arguments
    """
    print('Signal somar todas as linhas de extrato verbas\n\n')
    instance.gen_total_statements()
    instance.gen_total_integrations()
