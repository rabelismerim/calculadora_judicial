"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
from django.db import models
from django.db.models import FloatField, PositiveIntegerField
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from base.views import ExtractFormula
from calculation.comparative.signals import gen_statement_irrf
from calculation.funds.abstract.models import AbstractFunds, AbstractStatus
from core.abstract.models import AbstractModel
from rates.models import get_aliquot_by_tax, Rate


class FundIRRF(AbstractFunds):
    """
    This class represents a model for IRRF funds. It inherits from AbstractFunds and has
    the attributes 'taxable_amount' and 'months_period', which represent the taxable amount
    of the fund and the number of months in the investment period, respectively. The default
    value for 'taxable_amount' is 0, and the default value for 'months_period' is 1.
    Attributes:
        months_period (int): The number of months in the period for the IRRF calculation.
    """
    months_period = models.PositiveIntegerField(_('Months period'), default=1)

    def get_months_period(self) -> PositiveIntegerField:
        return self.months_period

    def get_total_funds(self):
        """
        This method returns the TotalValuesFunds object associated with the current fund object. If the object does
        not exist, it creates one and returns it.
        """
        if hasattr(self, 'totalvaluesirrf'):
            return self.totalvaluesirrf
        return TotalValuesIRRF.objects.get_or_create(fund=self)[0]

    def gen_total(self):
        """
        This method generates the total statements for the current fund by calling the set_total() method of the
        TotalValuesFunds object associated with it.
        """
        total_funds = self.get_total_funds()
        total_funds.set_total()

    def get_statements_values(self) -> list:
        return list(self.statementirrf_set.all().values_list('taxable_amounts', flat=True))

    def __delete_total_funds(self):
        if hasattr(self, 'totalvaluesirrf'):
            self.totalvaluesirrf.delete()

    def get_all_statement_irrf(self) -> list:
        """
        This method returns the TotalValuesFundsIntegrations object associated with the current fund object. If the
        object does not exist, it creates one and returns it.
        """
        return self.statementirrf_set.all()

    def delete(self, *args, **kwargs):
        """
        Deletes the Funds object, TotalValuesFunds and TotalValuesFundsIntegrations
        """
        for fund in self.get_all_statement_irrf():
            fund.delete(delete_total=False)
        self.__delete_total_funds()
        super(FundIRRF, self).delete(*args, **kwargs)


class StatementIRRF(AbstractModel):
    """
    This class represents a statement of taxable amounts for a given fund, used to calculate the Income Tax
    Withholding at Source (IRRF - Imposto de Renda Retido na Fonte in Portuguese) in Brazil. It is a subclass of
    AbstractStatement.

    In <Excel>, it refers to each piece of data that can be inserted in the base budget table for calculating budget
    sheets (irrf)

    Attributes:
        fund (ForeignKey): The foreign key to the Fund model, representing the fund associated with this statement.
        fund_name (CharField): The name of the fund associated with this statement.
        taxable_amounts (FloatField): The taxable amounts for this statement, used to calculate the IRFF.
    """
    fund = models.ForeignKey(FundIRRF, on_delete=models.PROTECT)
    fund_name = models.CharField(_('Fund'), max_length=150)
    taxable_amounts = models.FloatField(_('Taxable amounts'))

    def __str__(self):
        return f'{self.fund_name} | {self.fund} | {self.taxable_amounts}'

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the StatementFunds object and send a post-save signal.
        Args:
            send_signal_post_save (bool): Set to True to send a post-save signal. Default is True.
        """
        super(StatementIRRF, self).save(*args, **kwargs)
        if send_signal_post_save and self.fund.is_extraconcursal is False:
            gen_statement_irrf.send(sender=self.__class__, instance=self)

    def delete(self, delete_total=True, *args, **kwargs):
        """
        Deletes the StatementIRRF object and generates a new calculation of TotalValuesIRRF
        """
        fund = self.fund
        super(StatementIRRF, self).delete(*args, **kwargs)
        if delete_total:
            fund.gen_total()


class TotalValuesIRRF(AbstractStatus):
    """
    A class that represents the total values of IRRF (Income Tax on Individuals) for a fund.

    Attributes:
        taxable_amount (float): The taxable amount of the IRRF.
        taxable_portion (float): The taxable portion of the IRRF.
        aliquot (float): The aliquot of the IRRF.
        installment_deducted (float): The installment deducted from the IRRF.
        irrf_per_month (float): The value of the IRRF per month.
        irrf_per_period (float): The value of the IRRF for the entire period.
        fund (Funds): The fund to which the IRRF applies.
    """
    taxable_amount = models.FloatField(_('Taxable amount'), default=0)
    taxable_portion = models.FloatField(_('Taxable portion'), default=0)  # OK
    aliquot = models.FloatField(_('Aliquot'), default=0)  # OK
    installment_deducted = models.FloatField(_('Installment deducted'), default=0)  # OK
    irrf_per_month = models.FloatField(_('IRRF per month'), default=0)  # OK
    irrf_per_period = models.FloatField(_('IRRF per period'), default=0)  # OK
    fund = models.OneToOneField(FundIRRF, on_delete=models.PROTECT)

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the StatementFunds object and send a post-save signal.
        Args:
            send_signal_post_save (bool): Set to True to send a post-save signal. Default is True.
        """
        super(TotalValuesIRRF, self).save(*args, **kwargs)

    def __set_taxable_portion(self):
        self.taxable_portion = self.get_taxable_amount() / self.fund.get_months_period()

    def __set_aliquot(self, aliquot):
        self.aliquot = aliquot

    def __set_taxable_amount(self, taxable_amount):
        self.taxable_amount = taxable_amount

    def __set_installment_deducted(self, installment_deducted):
        self.installment_deducted = installment_deducted

    def __set_irrf_per_month(self, irrf_per_month):
        self.irrf_per_month = max(0, irrf_per_month)

    def __set_irrf_per_period(self, irrf_per_period):
        self.irrf_per_period = max(0, irrf_per_period)

    def get_taxable_amount(self) -> FloatField:
        return self.taxable_amount

    def get_taxable_portion(self):
        return self.taxable_portion

    def get_irrf_per_month(self):
        return self.irrf_per_month

    @property
    def total_corrected(self) -> float:
        return -1 * self.irrf_per_period

    def get_description(self):
        return self.fund.name

    def get_aliquot(self):
        return self.aliquot

    def get_installment_deducted(self):
        return self.installment_deducted

    def __str__(self):
        return f'{self.fund} | {self.taxable_amount} | {self.taxable_portion}'

    def __calc_irrf_per_month(self):
        taxable_portion: float = self.get_taxable_portion()
        aliquot: float = self.get_aliquot()
        deduction: float = self.get_installment_deducted()
        irrf_per_month: float = (taxable_portion * aliquot / 100) - deduction
        self.__set_irrf_per_month(irrf_per_month)

    def __calc_irrf_per_period(self):
        irrf_per_month = self.get_irrf_per_month()
        months_period = self.fund.get_months_period()
        self.__set_irrf_per_period(irrf_per_month * months_period)

    def __calc_taxable_amount(self):
        total = sum(self.fund.get_statements_values())
        self.__set_taxable_amount(total)

    def set_total(self):
        self.set_in_progress()

        self.__calc_taxable_amount()
        self.__set_taxable_portion()
        taxable_portion = self.get_taxable_portion()

        irrf = get_aliquot_by_tax(taxable_portion)
        if not irrf:
            self.set_error_aliquot()
            return

        self.__set_aliquot(irrf.aliquot)
        self.__set_installment_deducted(irrf.deduction)

        self.__calc_irrf_per_month()

        self.__calc_irrf_per_period()
        self.set_calculation_done()
        self.save()

    def delete(self, *args, **kwargs):
        """
        Deletes the Funds object, TotalValuesFunds and TotalValuesFundsIntegrations
        """
        statement_pfs = []
        statement_pfs_ids = []
        for description in self.fundsdescription_set.all():
            statement_pf = description.statement_pf
            description.delete()
            if not statement_pf.id in statement_pfs_ids:
                statement_pfs.append(statement_pf)
                statement_pfs_ids.append(statement_pf.id)
        for statement in statement_pfs:
            statement.calcule_total()
        super(TotalValuesIRRF, self).delete(*args, **kwargs)


@receiver(gen_statement_irrf, sender=StatementIRRF)
def save_statement_irrf(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementFunds object is saved. It
    calculates the monetary correction for the instance and generates the total statements of the related fund. It
    takes the sender and instance as arguments
    """
    print('Signal gerar linha extrato verbas irrf\n')

    instance.fund.gen_total()

    statement_methods = ['get_total_value', 'get_dsr_reflexes', 'get_monetary_correction', 'get_rate_by_date',
                         'calcule_monetary_correction', 'get_months_period', '__set_taxable_portion', '__set_aliquot',
                         '__set_taxable_amount', '__set_installment_deducted', '__set_irrf_per_month',
                         '__set_irrf_per_period', 'total_corrected', '__calc_irrf_per_month', '__calc_irrf_per_period',
                         '__calc_taxable_amount', 'get_aliquot', 'get_installment_deducted',
                         '_get_index_monetary_correction', 'get_corrected_value', 'get_data_base', 'get_total_value',
                         'get_historical_value', 'get_rate', 'save_total_funds', 'monetarycorrection', 'set_total',
                         '_calc_corrected_value', 'has_monetary_correction', '_calc_corrected_value', 'corrected_value']

    ExtractFormula(instance, instance.fund.calculation, statement_methods).get_methods(
        [StatementIRRF, FundIRRF, TotalValuesIRRF, Rate, save_statement_irrf])
