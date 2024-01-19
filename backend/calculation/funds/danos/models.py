"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

import datetime

from django.db import models
from django.db.models import TextChoices
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from base.views import ExtractFormula
from calculation.comparative.signals import gen_statement_danos, gen_statement_total_documents, update_calc
from calculation.funds.models import AbstractFunds, AbstractStatement, AbstractMonetaryCorrection, \
    AbstractTotalValuesFunds
from calculation.models import Calculation
from rates.models import Rate, CalculeRate


class InterestChoices(TextChoices):
    SIMPLES = 'S', _('Simples')
    SELIC_SIMPLES = 'E', _('Selic Simples')
    SELIC_COMPOSTA = 'C', _('Selic Composta')
    SELIC_RECEITA_FEDERAL = 'R', _('Selic Receita Federal')
    SEM_JUROS = 'N', _('Não há incidência de juros')


class FundDanos(AbstractFunds):
    # TODO: Adicionar campo fato gerador para verbas de danos morais(field description)
    type_interest = models.CharField(_('Tipo de juros'), max_length=1, choices=InterestChoices.choices,
                                     default=InterestChoices.SEM_JUROS)
    interest_initial_date = models.DateField(_('Data inicial do juros'))
    apply_monetary_correction = models.BooleanField(_('Aplicar Taxa?'), default=True)

    def get_total_funds(self, create=True):
        """
        This method returns the TotalValuesDanos object associated with the current fund object. If the object does
        not exist, it creates one and returns it.
        """
        total_values_danos = self.total_values_danos
        if total_values_danos:
            return total_values_danos
        if create:
            return TotalValuesDanos.objects.get_or_create(fund=self)[0]

    def gen_total(self):
        """
        This method generates the total statements for the current fund by calling the set_total() method of the
        TotalValuesDanos object associated with it.
        """
        total_funds = self.get_total_funds()
        total_funds.set_total()

    @property
    def total_values_danos(self):
        return getattr(self, 'totalvaluesdanos', None)

    def get_total_summed(self):
        """Get the corrected value of the sum of calculated sums"""
        return getattr(self.total_values_danos, 'total_corrected', 0)

    def get_total_historical_summed(self):
        """Get the corrected value of the sum of calculated sums"""
        return getattr(self.total_values_danos, 'total_historical', 0)

    def get_total_due_summed(self) -> float:
        """Get the corrected value of the sum of calculated sums"""
        return getattr(self.total_values_danos, 'total_due', 0)

    def get_total_total_default_interest(self) -> float:
        """Get the corrected value of the sum of calculated sums"""
        return getattr(self.total_values_danos, 'total_default_interest', 0)

    def get_statement(self):
        """
        This method returns the TotalValuesDanos object associated with the current fund object. If the object does
        not exist, it creates one and returns it.
        """
        return getattr(self, 'statementdanos', None)

    def delete(self, *args, **kwargs):
        """
        Deletes the StatementDanos object, FundDanos, MonetaryCorrection, FundsDocumentDescriptionPJ and
        generates a new calculation of TotalValuesDanos and StatementPJ
        """

        statement = self.get_statement()
        if statement:
            statement.delete(delete_fund=False)
        total_funds = self.get_total_funds(create=False)
        if total_funds:
            total_funds.delete()
        super(FundDanos, self).delete(*args, **kwargs)


class StatementDanos(AbstractStatement):
    """
    A model class that represents a financial statement for a fund.

    This class inherits from the AbstractStatement class and represents a financial statement for a fund. It has the
    same attributes as the AbstractStatement class, which include a Data base date, historical value, and a foreign
    key relationship to a Funds object.

    In <Excel>, it refers to each data that can be inserted in the document table on the accounting statement sheets (
    document)

    Attributes:
        This class has the same attributes as the AbstractStatement class.

    Methods:
        - `has_tax()` Return True if this statement has tax; False otherwise.
        - `__days360()` Return the number of days between the start_date and end_date using the 360-day method.
        - `days()` Return the number of days between the statement's data_base and the date_rj, if it exists and has tax
        - `_calc_default_interest()` Calculates the default interest based on the corrected value, default interest rate
            , and the number of days.
        - `default_interest()` Getter method for the default interest rate.
        - `total_due()` Calculates the total amount due, which is the sum of the fine, default interest, and corrected
            value.
        - `_calc_fine()` Calculates the fine to be charged based on the corrected value, fine rate, and default interest
        - `fine()` Getter method for the fine rate.
    """
    description = models.CharField(_('Deescrição do dano'), max_length=100)
    fund = models.OneToOneField(FundDanos, on_delete=models.CASCADE)

    def check_is_extraconcursal(self):
        return False

    def __str__(self):
        return f'{self.data_base} - {self.historical_value}'

    @property
    def interest_initial_date(self):
        return self.fund.interest_initial_date

    @property
    def name(self):
        return self.fund.name

    @property
    def monetary_correction(self):
        return self.get_monetary_correction()

    @staticmethod
    def __days360(start_date, end_date) -> int:
        """Return the number of days between the start_date and end_date using the 360-day method."""
        if start_date.day == 31:
            start_date = start_date.replace(day=30)
        if end_date.day == 31 and (start_date.day == 30 or start_date.day == 31):
            end_date = end_date.replace(day=30)
        elif end_date.day == 31:
            end_date = end_date.replace(day=1)
            end_date = end_date + datetime.timedelta(days=1)
        return (end_date.year - start_date.year) * 360 + \
            (end_date.month - start_date.month) * 30 + \
            (end_date.day - start_date.day)

    @property
    def days(self) -> int:
        """Return the number of days between the statement's data_base and the date_rj, if it exists and has tax."""
        data_base = self.get_data_base()
        date_rj = self.fund.calculation.get_date_rj()
        if not date_rj:
            self.set_error_rj()
            return 0
        return self.__days360(data_base, date_rj)

    @property
    def total_days(self) -> int:
        return self.days

    def get_percentage_default_interest(self) -> float:
        """
        Getter method for the default interest rate.

        :return:
            float: The default interest rate to be charged.
        """
        type_interest = self.fund.type_interest

        if type_interest == InterestChoices.SEM_JUROS:
            return 0

        interest_initial_date = self.fund.interest_initial_date
        data_rj = self.fund.calculation.get_date_rj()
        if not data_rj:
            self.set_error_rj()
            return 0

        if type_interest == InterestChoices.SIMPLES:
            days_360 = self.__days360(interest_initial_date, data_rj)
            indice = 1 / 30
            percentage_interest = days_360 * indice
            return percentage_interest

        selic = Rate.objects.filter(code=4390).first()
        calcule_rate = CalculeRate(filling_date=interest_initial_date, data_rj=data_rj, rate_selic=selic,
                                   rate_used=self.fund.rate)

        if type_interest == InterestChoices.SELIC_SIMPLES:
            percentage_interest = calcule_rate.calcule_simples()

        elif type_interest == InterestChoices.SELIC_COMPOSTA:
            percentage_interest = calcule_rate.calcule_composto()

        elif type_interest == InterestChoices.SELIC_RECEITA_FEDERAL:
            percentage_interest = calcule_rate.calcule_receita_federal()
        else:
            raise NotImplementedError('Tipo de juros não implementado')

        return percentage_interest

    @property
    def default_interest(self):
        """
        Getter method for the default interest rate.

        :return:
            float: The default interest rate to be charged.
        """

        interest_initial_date = self.fund.interest_initial_date
        data_rj = self.fund.calculation.get_date_rj()

        if interest_initial_date > data_rj:
            return 0

        percentage_interest = self.get_percentage_default_interest()
        corrected_value = self.get_corrected_value()

        if percentage_interest <= 0:
            return 0
        default_interest = percentage_interest * corrected_value / 100

        return default_interest

    @property
    def total_due(self) -> float:
        """
        Calculates the total amount due, which is the sum of the fine, default interest, and corrected value.

        :return:
            float: The total amount due.
        """
        return self.default_interest + self.get_corrected_value()

    def get_monetary_correction(self):
        """Returns the `monetarycorrectiondanos` attribute value"""
        return getattr(self, 'monetarycorrectiondanos', None)

    def create_monetary_correction(self, data: dict):
        """Create or update the MonetaryCorrection object"""
        MonetaryCorrectionDanos.objects.update_or_create(defaults=data, **{'statement': self})

    def calcule_monetary_correction(self):
        """
        Calculate the monetary correction and create the MonetaryCorrection object. If there is an error in the
        calculation, the MonetaryCorrection is excluded.
        """
        data: dict or None = self._get_index_monetary_correction()
        if data:
            self.create_monetary_correction(data)
            self.set_calculation_done()
        else:
            self.delete_monetary_correction()

    def delete_monetary_correction(self):
        """Delete the MonetaryCorrection object if exists"""
        monetary = self.get_monetary_correction()
        if monetary:
            monetary.delete()
        total_funds = self.fund.get_total_funds(create=False)
        if total_funds:
            total_funds.set_total()

    def get_corrected_value(self) -> float:
        """Returns corrected value if the monetary correction exists for the statement, else 0"""
        monetary_correction = getattr(self, 'monetarycorrectiondanos', None)
        if monetary_correction:
            return monetary_correction.corrected_value
        return 0

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the StatementDanos object and send a post-save signal.
        Args:
            send_signal_post_save (bool): Set to True to send a post-save signal. Default is True.
        """
        save = super(StatementDanos, self).save(*args, **kwargs)
        if send_signal_post_save:
            gen_statement_danos.send(sender=self.__class__, instance=self)

        return save

    def delete(self, delete_fund=True, *args, **kwargs):
        """
        Deletes the StatementDanos object, FundDanos, MonetaryCorrection, FundsDocumentDescriptionPJ and
        generates a new calculation of TotalValuesDanos and StatementPJ
        """
        self.set_calculation_in_delete()
        fund = self.fund  # FundDanos
        total = fund.get_total_funds()  # TotalValuesDanos
        self.delete_monetary_correction()  # MonetaryCorrection
        super(StatementDanos, self).delete(*args, **kwargs)

        if total and total.id:
            total.delete()
        if delete_fund:
            fund.delete()


class MonetaryCorrectionDanos(AbstractMonetaryCorrection):
    """
    A class that represents a monetary correction for a statement of integrations.

    In <Excel>, it refers to each piece of data that can be inserted in the document table on the accounting statement
    sheets (document)

    Attributes:
        statement (StatementDanos): The statement of integrations to which the monetary correction applies.
    """
    statement = models.OneToOneField(StatementDanos, on_delete=models.CASCADE)

    @property
    def corrected_value(self) -> float:
        """Returns corrected value calculated"""
        total_value = self._get_statement().get_total_value()
        if total_value == 0:
            return 0

        if self.statement.fund.apply_monetary_correction is False:
            return total_value
        return self.index_recovering / self.index_data_base * total_value


class TotalValuesDanos(AbstractTotalValuesFunds):
    """
    A class that represents the total values of a fund, which is a concrete implementation of AbstractTotalValuesFunds.

    Attributes:
        total_historical (float): The historical value of the fund.
        total_corrected (float): The corrected value of the fund.
        fund (Funds): The fund to which the values apply.

    Methods:
        __get_calculated_statement(): Returns the calculated statement of the fund.
        set_total(): Calculates and sets the total corrected and historical values of the fund based on the calculated
         statement.
    """
    fund = models.OneToOneField(FundDanos, on_delete=models.PROTECT)
    total_default_interest = models.FloatField(_('Total juros'), default=0)
    total_due = models.FloatField(_('Total due'), default=0)

    def __get_calculated_statement(self):
        """Returns the calculated statement of the fund."""
        return getattr(self.fund, 'statementdanos', None)

    def set_total(self):
        """
        Calculates and sets the total corrected, default_interest, fine and historical values of the fund based on
        the calculated statement.
        """
        statement = self.__get_calculated_statement()
        if statement and statement.id:
            self.total_historical = statement.get_total_value()
            self.total_corrected = statement.get_corrected_value()
            self.total_default_interest = statement.default_interest
            self.total_due = statement.total_due
        else:
            self.total_historical = 0
            self.total_corrected = 0
            self.total_default_interest = 0
            self.total_due = 0
        self.save()

    def save(self, *args, **kwargs):
        super(TotalValuesDanos, self).save()
        gen_statement_total_documents.send(sender=self.__class__, instance=self)


@receiver(gen_statement_danos, sender=StatementDanos)
def save_statement_documents(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementDanos object is saved. It
    calculates the monetary correction for the instance and generates the total document of the related fund. It
    takes the sender and instance as arguments
    """
    print('Signal gerar linha extrato verbas danos\n')
    instance.calcule_monetary_correction()
    instance.fund.gen_total()

    statement_methods = ['get_total_value', 'get_dsr_reflexes', 'get_monetary_correction',
                         'calcule_monetary_correction', 'get_monetary_correction', 'get_corrected_value',
                         'default_interest', 'get_total_due', 'get_fine', '__days360', 'has_tax',
                         'get_rate_by_date',
                         '_get_index_monetary_correction', 'get_corrected_value', 'get_data_base', 'get_total_value',
                         'get_historical_value', 'get_rate', 'save_total_funds', 'monetarycorrectiondanos', 'set_total',
                         '_calc_corrected_value', 'has_monetary_correction', '_calc_corrected_value', 'corrected_value']

    ExtractFormula(instance, instance.fund.calculation, statement_methods).get_methods(
        [StatementDanos, MonetaryCorrectionDanos, Rate, TotalValuesDanos, save_statement_documents])
    instance.fund.calculation.invalidate_calculation()


@receiver(update_calc, sender=Calculation)
def updated_calculation(sender, instance, **kwargs):
    """
    Signal handler for the update_calc event of a Calculation instance.

    Args:
    - sender: The model class that sent the signal (Calculation in this case).
    - instance (Calculation): The instance of Calculation that triggered the signal.
    - kwargs: Additional keyword arguments.
    """
    statements = StatementDanos.objects.filter(fund__calculation=instance)

    for statement in statements:
        statement.calcule_monetary_correction()

    total_funds = TotalValuesDanos.objects.filter(fund__calculation=instance)
    for total in total_funds:
        total.set_total()
