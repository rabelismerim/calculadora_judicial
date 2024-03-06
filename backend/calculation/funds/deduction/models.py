"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

import logging
import traceback

from django.db import models
from django.db.models import TextChoices
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from calculation.comparative.signals import gen_statement_documents
from calculation.funds.models import AbstractFunds, AbstractStatement, AbstractMonetaryCorrection, \
    AbstractTotalValuesFunds
from calculation.models import Calculation
from rates.models import Rate

CHOICES_STATUS_FUND_DEDUCTION = (('S', _('Requested')), ('C', _('Concluded')), ('E', _('In Progress')),
                                 ('F', _('Calculation failed - rate not found')),
                                 ('H', _('Calculation failed - rate data base not found')),
                                 ('R', _('Calculation failed - Saldo remanescente não encontrado')),
                                 ('P', _('Calculation failed - invalid parameters')),
                                 ('B', _('Calculation failed - in exclusion')),
                                 ('I', _('Registered')),
                                 ('J', _('Calculation failed - Rate SELIC not found')),
                                 )


class ChoicesStatusFundDeduction(TextChoices):
    REQUESTED = 'S', 'Requested'
    CONCLUDED = 'C', 'Concluded'
    IN_PROGRESS = 'I', 'In Progress'
    FAILED_RATE_NOT_FOUND = 'F', 'Calculation failed - rate not found'
    FAILED_RATE_DATE_BASE_NOT_FOUND = 'H', _('Calculation failed - rate data base not found')
    FAILED_DATE_BASE_NOT_FOUND = 'K', _('Calculation failed - data base not found')
    FAILED_PAYMENT_DATE_NOT_FOUND = 'N', _('Calculation failed - Data de pagamento não informada')
    FAILED_REMAIN_BALANCE_NOT_FOUND = 'D', _('Calculation failed - Saldo remanescente não encontrado')
    FAILED_NET_VALUE_NOT_FOUND = 'L', _('Calculation failed - Valor líquido não informado')
    FAILED_NOT_ADJUSTED_PAYMENT = 'A', _('Calculation failed - Pagamento ajustado não informado')
    FAILED_INVALID_PARAMETERS = 'P', _('Calculation failed - invalid parameters')
    FAILED_IN_EXCLUSION = 'B', _('Calculation failed - in exclusion')
    REGISTERED = 'R', _('Registered')
    FAILED_RATE_SELIC_NOT_FOUND = 'J', _('Calculation failed - Rate SELIC not found')


class FundDeduction(AbstractFunds):
    # Excel dedução - B15
    monetary_correction_update_date = models.DateField(_('Data da atualização da correção monetária'))
    interest_update_date = models.DateField(_('Data da atualização dos juros'))  # Excel dedução - B16
    approval_proposal_date = models.DateField(_('Data da homologação da proposta'))  # Excel dedução - B17
    fine = models.FloatField(_('Multa'), default=0)  # Excel dedução - B18
    default_interest = models.FloatField(_('Juros'), default=0)  # Excel dedução - B19

    def get_fine(self) -> float:
        """
        This method returns the fine amount for the current FundDeduction object

        Excel dedução - B20
        """
        return self.fine

    def get_default_interest(self) -> float:
        """
        This method returns the default interest amount for the current FundDeduction object.

        Excel dedução - B19
        """
        return self.default_interest

    def calcule_statement_deduction(self):
        deductions = self.statementdeduction_set.all().order_by('payment_date')
        deductions.update(used_remaining_balance=False)
        for current_deduction in deductions:
            current_deduction.save(send_signal_post_save=False)
        self.set_last_remaining_due()

    def get_total_legend(self):
        return 'Saldo remanescente de Honorários {}'

    def last_remaining(self):
        last = self.statementdeduction_set.all().order_by('payment_date').last()
        if last:
            if not last.use_remaining_balance:
                last.total_legend = self.get_total_legend().format(last.document)
                return last

    def get_last_remaining_due(self):
        return getattr(self, 'statementdeductiondue', None)

    def get_statementdeductiondue(self):
        last_remaining_due = self.get_last_remaining_due()
        data = []
        if last_remaining_due:
            data.append(last_remaining_due)
        return data

    def set_last_remaining_due(self):
        last: StatementDeduction = self.last_remaining()
        if last:
            defaults = {
                'data_base': last.payment_date,
                'document': last.document,
                'historical_value': last.remaining_balance,
            }

            deduction_due = StatementDeductionDue.objects.filter(fund=self).first()

            if not deduction_due:
                StatementDeductionDue.objects.create(fund=self, **defaults)
            else:
                deduction_due.dict_update(**defaults)

        else:
            last_remaining_due = self.get_last_remaining_due()
            if last_remaining_due:
                last_remaining_due.delete()


class AbstractStatementDeduction(AbstractStatement):
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
        - `days360()` Return the number of days between the start_date and end_date using the 360-day method.
        - `days()` Return the number of days between the statement's data_base and the date_rj, if it exists and has tax
        - `_calc_default_interest()` Calculates the default interest based on the corrected value, default interest rate
            , and the number of days.
        - `default_interest()` Getter method for the default interest rate.
        - `total_due()` Calculates the total amount due, which is the sum of the fine, default interest, and corrected
            value.
        - `_calc_fine()` Calculates the fine to be charged based on the corrected value, fine rate, and default interest
        - `fine()` Getter method for the fine rate.
    """
    CHOICES_STATUS_FUND = ChoicesStatusFundDeduction.choices
    document = models.CharField(_('Documento'), max_length=100)  # Excel dedução - A25
    index_data_base = models.FloatField(_('Índice na data base'), default=0, editable=False)  # Excel dedução - F25
    index_payment = models.FloatField(_('Índice na data de liquidação'), default=0,
                                      editable=False)  # Excel dedução - G25
    corrected_value = models.FloatField(_('Valor corrigido'), default=0, editable=False)  # Excel dedução - H25
    days = models.IntegerField(_('Dias'), default=0, editable=False)  # Excel dedução - I25
    default_interest = models.FloatField(_('Juros devido'), default=0, editable=False)  # Excel dedução - J25
    fine = models.FloatField(_('Multa devida'), default=0, editable=False)  # Excel dedução - K25

    def __str__(self):
        return f'{self.name} - {self.data_base} - {self.historical_value}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_remain_balance = None

    def check_is_extraconcursal(self):
        return False

    @property
    def name(self):
        return self.fund.name

    def calc_index(self):
        """Returns index data base

        Excel dedução - F25

        =SE(G25/F25*E25<E25;E25;G25/F25*E25)
        """
        self.index_data_base, self.index_payment = self.get_index_monetary_correction()

    @property
    def total_due(self) -> float:
        """
        Calculates the total amount due, which is the sum of the fine, default interest, and corrected value.

        :return:
            float: The total amount due.
        """
        return self.fine + self.default_interest + self.corrected_value

    def set_payment_date_not_found(self):
        """Sets the status of the calculation to FAILED_PAYMENT_DATE_NOT_FOUND"""
        self._set_status(ChoicesStatusFundDeduction.FAILED_PAYMENT_DATE_NOT_FOUND)

    def set_date_base_not_found(self):
        """Sets the status of the calculation to FAILED_DATE_BASE_NOT_FOUND"""
        self._set_status(ChoicesStatusFundDeduction.FAILED_DATE_BASE_NOT_FOUND)

    def set_remain_balance_not_found(self):
        """Sets the status of the calculation to FAILED_REMAIN_BALANCE_NOT_FOUND"""
        self._set_status(ChoicesStatusFundDeduction.FAILED_REMAIN_BALANCE_NOT_FOUND)

    def set_net_value_not_found(self):
        """Sets the status of the calculation to FAILED_NET_VALUE_NOT_FOUND"""
        self._set_status(ChoicesStatusFundDeduction.FAILED_NET_VALUE_NOT_FOUND)

    def set_adjusted_payment_not_found(self):
        """Sets the status of the calculation to FAILED_NOT_ADJUSTED_PAYMENT"""
        self._set_status(ChoicesStatusFundDeduction.FAILED_NOT_ADJUSTED_PAYMENT)

    class Meta:
        abstract = True


class StatementDeduction(AbstractStatementDeduction):
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
        - `days360()` Return the number of days between the start_date and end_date using the 360-day method.
        - `days()` Return the number of days between the statement's data_base and the date_rj, if it exists and has tax
        - `_calc_default_interest()` Calculates the default interest based on the corrected value, default interest rate
            , and the number of days.
        - `default_interest()` Getter method for the default interest rate.
        - `total_due()` Calculates the total amount due, which is the sum of the fine, default interest, and corrected
            value.
        - `_calc_fine()` Calculates the fine to be charged based on the corrected value, fine rate, and default interest
        - `fine()` Getter method for the fine rate.
    """
    fund = models.ForeignKey(FundDeduction, on_delete=models.PROTECT)
    net_value = models.FloatField(_('Valor líquido'), default=None, null=True, blank=True)  # Excel dedução - E25
    remaining_balance = models.FloatField(_('Saldo remanescente'), default=0, editable=False)  # Excel dedução - M25
    use_remaining_balance = models.BooleanField(_('Usar saldo remanescente'), default=False, editable=False)
    used_remaining_balance = models.BooleanField(_('Saldo remanescente utilizado'), default=False, editable=False)
    payment_date = models.DateField(_('Data de pagamento'), null=True, blank=True)  # Excel dedução - C25
    adjusted_payment = models.FloatField(_('Pagamento ajustado'), default=0, null=True,
                                         blank=True)  # Excel dedução - L25

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the StatementDeduction object and send a post-save signal.
        Args:
            send_signal_post_save (bool): Set to True to send a post-save signal. Default is True.
        """

        try:
            if not self.id or not self.created_at:
                self.use_remaining_balance = not isinstance(self.net_value, (float, int))
                self.calc_payment_date()
            self.calc_net_value()
            self.calc_days()
            self.calc_index()
            self.calc_corrected_value()
            self.calc_default_interest()
            self.calc_fine()
            self.calc_adjusted_payment()
            self.calc_remaining_balance()
            self.set_calculation_done()
        except ValueError as e:

            traceback_str = traceback.format_exc()
            logging.error(f'traceback_str: {traceback_str}')

            logging.error(e, exc_info=True)
            self.set_error_parameters()

        save = super().save(*args, **kwargs)
        if send_signal_post_save:
            gen_statement_documents.send(sender=self.__class__, instance=self)
        return save

    def calc_remaining_balance(self):
        """
        Getter method for the remaining balance.

        Excel dedução - M25
        =SOMA(H25;J25;K25)+L25
        """
        corrected_value = self.corrected_value
        default_interest = self.default_interest
        fine = self.fine
        adjusted_payment = self.adjusted_payment or 0
        self.remaining_balance = corrected_value + fine + default_interest + adjusted_payment

    def calc_default_interest(self):
        """
        Calculates the default interest based on the corrected value, default interest rate, and the number of days.

        Excel dedução - J25
        =I25*($B$19/30)*H25
        """

        default_interest = self.fund.default_interest
        corrected_value = self.corrected_value
        if corrected_value * self.days * default_interest == 0:
            self.default_interest = 0
        else:
            self.default_interest = (corrected_value * (default_interest / 30) * self.days) / 100

    def calc_days(self):
        """Calcule the number of days between the statement's data_base and the payment_date.

        Excel dedução - I25
        =SE(DIAS360(B25;C25)>=0;DIAS360(B25;C25);0)
        """
        data_base = self.data_base
        payment_date = self.payment_date

        days = self.days360(data_base, payment_date)

        if days > 0:
            self.days = days
        else:
            self.days = 0

    def get_index_monetary_correction(self) -> dict or None:
        """Retrieves the monetary correction from a financial statement. It gets the calculation, data and rate
        information and then validates the date and rate. The index_data_base and index_recovering are returned as a
        dictionary. """
        data_base = self.data_base
        payment_date = self.payment_date
        rate = self.fund.get_rate()

        rate_data_base = rate.get_rate_by_date(data_base)
        rate_payment_date = rate.get_rate_by_date(payment_date)

        if rate_data_base.rate.initial_accumulated or rate_data_base.rate.start_indice:  # Calculo feito pelo acumulado
            rate_data_base_accumulated = rate_data_base.get_accumulated
            rate_payment_accumulated_date = rate_payment_date.get_accumulated
            return rate_data_base_accumulated, rate_payment_accumulated_date
        return rate_data_base.value, rate_payment_date.value

    def calc_fine(self):
        """
        Calculates the fine to be charged based on the corrected value, fine rate, and default interest.

        Excel dedução - K25
        =(H25+J25)*$B$20

        or

        Excel dedução - K26
        =(H26+J26-M25)*$B$20
        """
        fine = self.fund.fine
        corrected_value = self.corrected_value
        default_interest = self.default_interest

        if self.use_remaining_balance:
            net_value = self.net_value
            value = (corrected_value + default_interest - net_value) * fine
        else:
            value = (corrected_value + default_interest) * fine
        if value == 0:
            self.fine = 0
        else:
            self.fine = value / 100

    def calc_net_value(self):
        """
        Getter method for the remaining balance.

        Excel dedução - M25
        =SOMA(H25;J25;K25)+L25
        """

        if not self.use_remaining_balance:

            if not self.net_value:
                self.set_net_value_not_found()
                raise ValueError(ChoicesStatusFundDeduction.FAILED_NET_VALUE_NOT_FOUND)
            return

        previous_statement = self.get_previous_statement()
        if not previous_statement:
            self.set_remain_balance_not_found()
            raise ValueError(ChoicesStatusFundDeduction.FAILED_REMAIN_BALANCE_NOT_FOUND)
        self.net_value = previous_statement.remaining_balance
        self.data_base = previous_statement.payment_date
        self.historical_value = 0

    def get_previous_statement(self):
        if self._previous_remain_balance:
            return self._previous_remain_balance

        payment_date = self.payment_date

        if not payment_date:
            previous_remain_balance = self.fund.statementdeduction_set.order_by('-payment_date').first()
        else:

            if self.use_remaining_balance:
                filters = {'payment_date__lt': payment_date, 'use_remaining_balance': False}

            else:
                filters = {'payment_date__lte': payment_date}

            previous_remain_balance = self.fund.statementdeduction_set.exclude(id=self.id).filter(**filters).order_by(
                '-payment_date').first()

            if self.use_remaining_balance and previous_remain_balance:

                if previous_remain_balance.used_remaining_balance:
                    self.set_remain_balance_not_found()
                    raise ValueError(ChoicesStatusFundDeduction.FAILED_REMAIN_BALANCE_NOT_FOUND.name)
                else:
                    StatementDeduction.objects.filter(id=previous_remain_balance.id).update(used_remaining_balance=True)

        self._previous_remain_balance = previous_remain_balance
        return previous_remain_balance

    def calc_payment_date(self):
        """
        Getter method for the remaining balance.

        Excel dedução - M25
        =SOMA(H25;J25;K25)+L25
        """

        if not self.use_remaining_balance:
            previous_statement = self.get_previous_statement()
            if not previous_statement and not self.payment_date:
                self.set_payment_date_not_found()
                raise ValueError(ChoicesStatusFundDeduction.FAILED_REMAIN_BALANCE_NOT_FOUND.name)

            if previous_statement:
                self.payment_date = previous_statement.payment_date

        elif not self.payment_date:
            self.set_payment_date_not_found()
            raise ValueError(ChoicesStatusFundDeduction.FAILED_REMAIN_BALANCE_NOT_FOUND.name)

    def calc_adjusted_payment(self):
        """
        Getter method for the remaining balance.

        Excel dedução - M25
        =SOMA(H25;J25;K25)+L25
        """
        has_statement = self.fund.statementdeduction_set.exclude(id=self.id).exists()

        first_statement = self.fund.statementdeduction_set.order_by('payment_date').first()

        if has_statement is False or (first_statement and first_statement.id == self.id):
            self.adjusted_payment = -1 * self.net_value
            return

        if self.use_remaining_balance:
            if not self.adjusted_payment:
                self.set_adjusted_payment_not_found()
                raise ValueError(ChoicesStatusFundDeduction.FAILED_NOT_ADJUSTED_PAYMENT.name)
            return

        previous_statement = self.get_previous_statement()
        if not previous_statement:
            self.set_remain_balance_not_found()
            raise ValueError(ChoicesStatusFundDeduction.FAILED_REMAIN_BALANCE_NOT_FOUND.name)

        self.adjusted_payment = previous_statement.remaining_balance

    def calc_corrected_value(self):
        """Returns corrected value calculated

        Excel dedução - H25

        =SE(G25/F25*E25<E25;E25;G25/F25*E25)
        """
        net_value = self.net_value
        if net_value == 0:
            self.corrected_value = 0

        corrected_value = self.index_payment / self.index_data_base * net_value

        if corrected_value < net_value:
            self.corrected_value = net_value
        else:
            self.corrected_value = corrected_value


class StatementDeductionDue(AbstractStatementDeduction):
    fund = models.OneToOneField(FundDeduction, on_delete=models.PROTECT)

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the StatementDeduction object and send a post-save signal.
        Args:
            send_signal_post_save (bool): Set to True to send a post-save signal. Default is True.
        """

        try:
            self.calc_days()
            self.calc_index()
            self.calc_corrected_value()
            self.calc_default_interest()
            self.calc_fine()
            self.set_calculation_done()
        except ValueError as e:
            traceback_str = traceback.format_exc()
            logging.error(f'traceback_str: {traceback_str}')

            logging.error(e, exc_info=True)
            self.set_error_parameters()

        save = super().save(*args, **kwargs)
        return save

    def calc_fine(self):
        self.fine = 0

    def calc_days(self):
        """Calcule the number of days between the statement's data_base and the payment_date.

        Excel dedução - I25
        =SE(DIAS360(B25;C25)>=0;DIAS360(B25;C25);0)
        """
        data_base = self.data_base
        payment_date = self.fund.interest_update_date

        days = self.days360(data_base, payment_date)

        if days > 0:
            self.days = days
        else:
            self.days = 0

    def get_index_monetary_correction(self) -> dict or None:
        """Retrieves the monetary correction from a financial statement. It gets the calculation, data and rate
        information and then validates the date and rate. The index_data_base and index_recovering are returned as a
        dictionary. """
        data_base = self.data_base
        payment_date = self.fund.monetary_correction_update_date
        rate = self.fund.get_rate()

        rate_data_base = rate.get_rate_by_date(data_base)
        rate_payment_date = rate.get_rate_by_date(payment_date)

        if rate_data_base.rate.initial_accumulated or rate_data_base.rate.start_indice:  # Calculo feito pelo acumulado
            rate_data_base_accumulated = rate_data_base.get_accumulated
            rate_payment_accumulated_date = rate_payment_date.get_accumulated
            return rate_data_base_accumulated, rate_payment_accumulated_date
        return rate_data_base.value, rate_payment_date.value

    def calc_corrected_value(self):
        """Returns corrected value calculated

        Excel dedução - H46

        =SE(E46/D46*C46<C46;C46;E46/D46*C46)
        """
        net_value = self.historical_value
        corrected_value = self.index_payment / self.index_data_base * net_value

        if corrected_value < net_value:
            self.corrected_value = net_value
        else:
            self.corrected_value = corrected_value

    @property
    def historical_charges(self) -> float:
        """
        Calculates the Historical Charges.

        Excel dedução - J46
        return 0
        """
        return 0

    def calc_default_interest(self):
        """
        Calculates the fine to be charged based on the corrected value, fine rate, and default interest.

        Excel dedução - K25
        =(H25+J25)*$B$20

        or

        Excel dedução - K26
        =(H26+J26-M25)*$B$20
        """
        default_interest = self.fund.default_interest
        corrected_value = self.corrected_value
        days = self.days
        self.default_interest = (days * (default_interest / 30) * corrected_value) / 100

    @property
    def total_due(self) -> float:
        """
        Calculates Total due.

        Excel dedução - K46
        =SUM(F46;H46;I46;J46)
        """
        return self.corrected_value + self.fine + self.default_interest + self.historical_charges


@receiver(gen_statement_documents, sender=StatementDeduction)
def save_statement_documents(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementDeduction object is saved. It
    calculates the monetary correction for the instance and generates the total document of the related fund. It
    takes the sender and instance as arguments
    """
    print('Signal gerar linha extrato verbas Dedução\n')
    instance.fund.calcule_statement_deduction()
