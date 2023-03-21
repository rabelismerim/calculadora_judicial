"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
from django.db import models
from django.db.models import FloatField
from django.utils.translation import gettext_lazy as _

from calculation.funds.abstract.models import AbstractFunds
from core.abstract.models import AbstractModel


class FundIRRF(AbstractFunds):
    class Meta:
        verbose_name = _('Fund IRRF')
        verbose_name_plural = _('Funds IRRF')

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
    fund_name = models.CharField(_('Verbas'), max_length=150)
    taxable_amounts = models.FloatField(_('Valores tributáveis'))

    class Meta:
        verbose_name = _('Statement IRRF')
        verbose_name_plural = _('Statements IRRF')


class TotalValuesIRRF(AbstractModel):
    """
    A class that represents the total values of IRRF (Income Tax on Individuals) for a fund.

    Attributes:
        taxable_amount (float): The taxable amount of the IRRF.
        months_period (int): The number of months in the period for the IRRF calculation.
        taxable_portion (float): The taxable portion of the IRRF.
        aliquot (float): The aliquot of the IRRF.
        installment_deducted (float): The installment deducted from the IRRF.
        irrf_per_month (float): The value of the IRRF per month.
        irrf_per_period (float): The value of the IRRF for the entire period.
        fund (Funds): The fund to which the IRRF applies.
    """
    taxable_amount = models.FloatField(_('Valor tributável'), default=0)
    months_period = models.PositiveIntegerField(_('Meses no período'))
    taxable_portion = models.FloatField(_('Parcela tributável'), default=0)
    aliquot = models.FloatField(_('Alíquota'), default=0)
    installment_deducted = models.FloatField(_('Parcela a deduzir'), default=0)
    irrf_per_month = models.FloatField(_('Valor IRRF por mês'), default=0)
    irrf_per_period = models.FloatField(_('Valor do IRRF no período'), default=0)
    fund = models.OneToOneField(FundIRRF, on_delete=models.PROTECT)
    total = models.FloatField(_('Total da soma dos valores'), default=0)

    def __str__(self):
        return f'{self.fund} - {self.taxable_amount}'

    class Meta:
        verbose_name = _('Total value IRRF')
        verbose_name_plural = _('Total values IRRF')
