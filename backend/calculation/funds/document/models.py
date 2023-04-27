"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

import datetime

from django.db import models, transaction
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from base.views import ExtractFormula
from calculation.comparative.signals import gen_statement_documents, gen_statement_total_documents
from calculation.funds.models import AbstractFunds, AbstractStatement, AbstractMonetaryCorrection, \
    AbstractTotalValuesFunds
from rates.models import Rate


class FundDocument(AbstractFunds):
    # Pode haver multas por atraso de pagamento. Nesse caso a nota fiscal estabelece um valor personalizado
    fine = models.FloatField(_('Fine'), default=0)
    has_custom_fine = models.BooleanField(_('Has custom fine invoices'), default=False)

    def get_total_funds(self):
        """
        This method returns the TotalValuesDocument object associated with the current fund object. If the object does
        not exist, it creates one and returns it.
        """
        if hasattr(self, 'totalvaluesdocument'):
            return self.totalvaluesdocument
        return TotalValuesDocument.objects.get_or_create(fund=self)[0]

    def get_fine(self) -> float:
        """
        This method returns the fine amount for the current FundDocument object. If the has_custom_fine flag is set to
        True, it returns the custom fine value specified in the invoice. If not, it calculates the fine amount using
        the calculation object associated with the current fund and returns it.
        """
        if self.has_custom_fine:
            return self.fine
        return self.calculation.get_fine()

    def gen_total(self):
        """
        This method generates the total statements for the current fund by calling the set_total() method of the
        TotalValuesDocument object associated with it.
        """
        total_funds = self.get_total_funds()
        total_funds.set_total()


class StatementDocument(AbstractStatement):
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
    number = models.CharField(_('Document number'), max_length=100)
    fund = models.OneToOneField(FundDocument, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.data_base} - {self.historical_value}'

    def has_tax(self):
        """Return True if this statement has tax; False otherwise."""
        data_base = self.get_data_base()
        date_rj = self.fund.calculation.get_date_rj()
        if not date_rj:
            self.set_error_rj()
            return False
        return data_base <= date_rj

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
        if self.has_tax():
            data_base = self.get_data_base()
            date_rj = self.fund.calculation.get_date_rj()
            if not date_rj:
                self.set_error_rj()
                return 0
            return self.__days360(data_base, date_rj)
        return 0

    @staticmethod
    def _calc_default_interest(corrected_value, default_interest, days) -> float:
        """
        Calculates the default interest based on the corrected value, default interest rate, and the number of days.

        Args:
           corrected_value (float): The corrected value of the debt.
           default_interest (float): The default interest rate.
           days (int): The number of days the debt is overdue.

        Returns:
           float: The amount of default interest to be charged.
        """
        return (corrected_value * (default_interest / 30) * days) / 100

    @property
    def default_interest(self):
        """
        Getter method for the default interest rate.

        Returns:
            float: The default interest rate to be charged.
        """
        default_interest = self.fund.calculation.get_default_interest()
        corrected_value = self.get_corrected_value()
        if corrected_value * self.days * default_interest == 0:
            return 0
        return self._calc_default_interest(corrected_value, default_interest, self.days)

    @property
    def total_due(self) -> float:
        """
        Calculates the total amount due, which is the sum of the fine, default interest, and corrected value.

        Returns:
            float: The total amount due.
        """
        return sum([self.get_fine(), self.get_default_interest(), self.get_corrected_value()])

    @staticmethod
    def _calc_fine(corrected_value, fine, default_interest) -> float:
        """
        Calculates the fine to be charged based on the corrected value, fine rate, and default interest.

        Args:
            corrected_value (float): The corrected value of the debt.
            fine (float): The fine rate.
            default_interest (float): The default interest rate.

        Returns:
            float: The amount of fine to be charged.
        """
        return (corrected_value + default_interest * fine) / 100

    @property
    def fine(self):
        """
        Getter method for the fine rate.

        Returns:
            float: The fine rate to be charged.
        """
        fine = self.fund.get_fine()
        corrected_value = self.get_corrected_value()
        default_interest = self.default_interest
        if corrected_value * default_interest * fine == 0:
            return 0
        return self._calc_fine(corrected_value, fine, default_interest)

    def has_monetary_correction(self) -> bool:
        """Returns True if the monetary correction exists for the statement."""
        return hasattr(self, 'monetarycorrectiondocument')

    def get_monetary_correction(self):
        """Returns the `monetarycorrection` attribute value"""
        if self.has_monetary_correction():
            return self.monetarycorrectiondocument

    def create_monetary_correction(self, data: dict):
        """Create or update the MonetaryCorrection object"""
        MonetaryCorrectionDocument.objects.update_or_create(defaults=data, **{'statement': self})

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

    def get_corrected_value(self) -> float:
        """Returns corrected value if the monetary correction exists for the statement, else 0"""
        if self.has_monetary_correction():
            return self.monetarycorrectiondocument.corrected_value
        return 0

    def get_default_interest(self) -> float:
        """Returns default interest value for the statement"""
        return self.default_interest

    def get_total_due(self) -> float:
        """Returns total_due value for the statement"""
        return self.total_due

    def get_fine(self) -> float:
        """Returns fine value for the statement"""
        return self.fine

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the StatementDocument object and send a post-save signal.
        Args:
            send_signal_post_save (bool): Set to True to send a post-save signal. Default is True.
        """
        super(StatementDocument, self).save(*args, **kwargs)
        if send_signal_post_save and self.fund.is_extraconcursal is False:
            gen_statement_documents.send(sender=self.__class__, instance=self)

    def delete(self, *args, **kwargs):
        """
        Deletes the StatementDocument object, FundDocument, MonetaryCorrection, FundsDocumentDescriptionPJ and
        generates a new calculation of TotalValuesDocument and StatementPJ
        """
        self.set_calculation_in_delete()
        fund = self.fund  # FundDocument
        total = fund.get_total_funds()  # TotalValuesDocument
        self.delete_monetary_correction()  # MonetaryCorrection
        super(StatementDocument, self).delete(*args, **kwargs)

        description_doc = total.get_description_doc()  # FundsDocumentDescriptionPJ
        if description_doc:
            statement_pj = description_doc.statement_pj  # StatementPJ
            description_doc.delete()
            statement_pj.set_total()
        total.delete()
        fund.delete()


class MonetaryCorrectionDocument(AbstractMonetaryCorrection):
    """
    A class that represents a monetary correction for a statement of integrations.

    In <Excel>, it refers to each piece of data that can be inserted in the document table on the accounting statement
    sheets (document)

    Attributes:
        statement (StatementIntegrations): The statement of integrations to which the monetary correction applies.
    """
    statement = models.OneToOneField(StatementDocument, on_delete=models.PROTECT)

    @property
    def corrected_value(self) -> float:
        """Returns corrected value calculated"""
        total_value = self._get_statement().get_total_value()
        if total_value == 0:
            return 0
        return self.index_recovering / self.index_data_base * total_value


class TotalValuesDocument(AbstractTotalValuesFunds):
    """
    A class that represents the total values of a fund, which is a concrete implementation of AbstractTotalValuesFunds.

    Attributes:
        total_historical (float): The historical value of the fund.
        total_corrected (float): The corrected value of the fund.
        total_dsr_reflexes (float): The drs reflexes value of the fund.
        total_accurate (float): The total accurate value of the fund.
        fund (Funds): The fund to which the values apply.

    Methods:
        __get_calculated_statement(): Returns the calculated statement of the fund.
        set_total(): Calculates and sets the total corrected and historical values of the fund based on the calculated
         statement.
    """
    fund = models.OneToOneField(FundDocument, on_delete=models.PROTECT)
    total_default_interest = models.FloatField(_('Total juros'), default=0)
    total_fine = models.FloatField(_('Total multa'), default=0)
    total_due = models.FloatField(_('Total due'), default=0)

    def __get_calculated_statement(self):
        """Returns the calculated statement of the fund."""
        if hasattr(self.fund, 'statementdocument') and self.fund.statementdocument.status == 'C':
            return self.fund.statementdocument

    def get_description_doc(self):
        """Returns the calculated FundsDocumentDescriptionPJ of the total obj."""
        if hasattr(self, 'fundsdocumentdescriptionpj'):
            return self.fundsdocumentdescriptionpj

    def set_total(self):
        """
        Calculates and sets the total corrected, default_interest, fine and historical values of the fund based on
        the calculated statement.
        """
        statement = self.__get_calculated_statement()
        if statement and statement.id:
            self.total_historical = statement.get_total_value()
            self.total_corrected = statement.get_corrected_value()
            self.total_default_interest = statement.get_default_interest()
            self.total_fine = statement.get_fine()
            self.total_due = statement.get_total_due()
        else:
            self.total_historical = 0
            self.total_corrected = 0
            self.total_default_interest = 0
            self.total_fine = 0
            self.total_due = 0
        self.save()

    def save(self, *args, **kwargs):
        super(TotalValuesDocument, self).save()
        gen_statement_total_documents.send(sender=self.__class__, instance=self)


@receiver(gen_statement_documents, sender=StatementDocument)
def save_statement_documents(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementDocument object is saved. It
    calculates the monetary correction for the instance and generates the total document of the related fund. It
    takes the sender and instance as arguments
    """
    print('Signal gerar linha extrato verbas documentos\n')
    instance.calcule_monetary_correction()
    instance.fund.gen_total()

    statement_methods = ['get_total_value', 'get_dsr_reflexes', 'get_monetary_correction',
                         'calcule_monetary_correction', 'get_monetary_correction', 'get_corrected_value',
                         'get_default_interest', 'get_total_due', 'get_fine', '__days360', 'has_tax',
                         'get_rate_by_date',
                         '_get_index_monetary_correction', 'get_corrected_value', 'get_data_base', 'get_total_value',
                         'get_historical_value', 'get_rate', 'save_total_funds', 'monetarycorrection', 'set_total',
                         '_calc_corrected_value', 'has_monetary_correction', '_calc_corrected_value', 'corrected_value']

    ExtractFormula(instance, instance.fund.calculation, statement_methods).get_methods(
        [StatementDocument, MonetaryCorrectionDocument, Rate, TotalValuesDocument, save_statement_documents])
