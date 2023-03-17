"""
Defines models for financial statements and funds.

AbstractModel is inherited for common fields such as id, created_at, and updated_at.
Funds class is used to represent a financial fund with a name and calculation.
AbstractStatement class is an abstract model used to represent a financial statement,
with fields for a Data base date, historical value, and a foreign key to Funds.
StatementFunds class extends AbstractStatement to represent a statement related to funds.
StatementIntegrations extends AbstractStatement and includes a description field.
"""
import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from calculation.comparative.signals import gen_total_statement_funds, gen_statement_funds, gen_total_funds
from calculation.models import Calculation
from core.abstract.models import AbstractModel
from dateutil.relativedelta import relativedelta


class Funds(AbstractModel):
    """
    A model class that represents Funds.

    This class inherits from the AbstractModel class and represents a fund with a name and a foreign key relationship
    to a Calculation object. The 'name' attribute is a character field with a maximum length of 50, and represents
    the name of the fund. The 'calculation' attribute is a foreign key relationship to a Calculation object and
    ensures that the relationship is protected upon deletion.

    In <<Excel>>, it refers to the budget sheets (tst, irrf, moral damages, etc.)

    Attributes: name (CharField): Represents the name of the fund. calculation (ForeignKey):
    Represents a foreign key relationship to a Calculation object.

    Methods:
    This class does not define any methods.
    """

    name = models.CharField(_('Nome das verbas'), max_length=50)
    calculation = models.ForeignKey(Calculation, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Fund')
        verbose_name_plural = _('Funds')

    def __str__(self):
        return self.name

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


CHOICES_STATUS_FUND = (('S', _('Solicitado')), ('C', _('Concluído')), ('E', _('Em Progresso')),
                       ('F', _('Falha no cálculo - índice não encontrado')), ('R', _('Falha no cálculo - sem data RJ')))


class AbstractStatement(AbstractModel):
    """
    The `AbstractStatement` class represents an abstract financial statement model with features such as `data_base`
    field that represents the date of the statement, `historical_value` field that represents the historical value of
    the statement, and `fund` field that is a foreign key to a `Funds` object. This is an abstract class and inherits
    from `AbstractModel`.

    Attributes:
    - `data_base` (DateField): Represents the date of the financial statement.
    - `historical_value` (FloatField): Represents the historical value of the statement.
    - `funds` (ForeignKey): Represents a foreign key relationship to a `Funds` object.

    Methods:
    - `set_in_progress()` sets the status of the calculation to 'E'.
    - `set_error_rj()` sets the status of the calculation to 'R'.
    - `set_error_indice()` sets the status of the calculation to 'F'.
    - `set_calculation_done()` sets the status of the calculation to 'C'.
    - `_check_status_choice(value: str)` checks if the status value provided is valid.
    - `_set_status(value: str)` sets the status of the calculation.
    - `_get_monetary_correction()` returns the monetary correction based on `data_base`, `date_rj`, and `rate` fields.
    - `get_data_base()` returns the `data_base` attribute with or without a summary applied.
    - `get_historical_value()` returns the `historical_value` attribute value.
    """
    data_base = models.DateField('Data base')
    historical_value = models.FloatField(_('Valor histórico'))

    # Sumula 381 se refere a cálculos trabalhistas em que o pagamento de salário se dá no mês subsequente ao trabalhado.
    # Sendo necessário adicionar um mês na hora de calcular o valor
    # TODO: Verificar automaticamente se é ou não verba para aplicar a sumula
    summary = models.BooleanField(_('Aplicar súmula 381?'), default=False)
    fund = models.ForeignKey(Funds, on_delete=models.PROTECT)
    status = models.CharField(_('Status do cálculo'), max_length=1, choices=CHOICES_STATUS_FUND, default='S')

    def set_in_progress(self):
        """Sets the status of the calculation to 'E'."""
        self._set_status('E')

    def set_error_rj(self):
        """Sets the status of the calculation to 'R'."""
        self._set_status('R')

    def set_error_indice(self):
        """Sets the status of the calculation to 'F'."""
        self._set_status('F')

    def set_calculation_done(self):
        """Sets the status of the calculation to 'C'."""
        self._set_status('C')

    @staticmethod
    def _check_status_choice(value: str):
        """Checks if the status value provided is valid"""
        has_value = False
        for string, legend in CHOICES_STATUS_FUND:
            if value == string:
                has_value = True
                break
        if not has_value:
            raise ValueError(_(f'O status {value} não corresponde a nenhum status válido'))

    def _set_status(self, value: str):
        """Sets the status of the calculation"""
        # override method in inheritance
        raise NotImplementedError('override method in inheritance')

    def _get_monetary_correction(self) -> dict or None:
        """Retrieves the monetary correction from a financial statement. It gets the calculation, data and rate
        information and then validates the date and rate. The index_data_base and index_recovering are returned as a
        dictionary. """
        statement = self
        calculation = statement.fund.calculation
        statement.set_in_progress()
        data_base = statement.get_data_base()
        date_rj = calculation.get_date_rj()
        rate = calculation.get_rate()

        if not date_rj:
            statement.set_error_rj()
            return None

        rate_data_base = rate.get_rate_by_date(data_base)
        rate_date_rj = rate.get_rate_by_date(date_rj)

        if not rate_date_rj or not rate_data_base:
            statement.set_error_indice()
            return None

        data = {
            'index_data_base': rate_data_base.value,
            'index_recovering': rate_date_rj.value,
        }
        return data

    def get_data_base(self):
        """
        Returns the data base based on the "summary" attribute.
        If "summary" is True, returns the data base increased by one month using relativedelta function.
        If "summary" is False, returns the current data base.
        Returns:
            datetime object: The data base.
        """
        if self.summary:
            return self.data_base + relativedelta(months=1)
        return self.data_base

    def get_historical_value(self):
        """Returns the `historical_value` attribute value"""
        return self.historical_value

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.data_base} - {self.historical_value}'


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

    Methods:
    - has_monetary_correction(self) -> bool: Returns True if the monetary correction exists for the statement.
    - _set_status(self, value: str): Sets the status of the statement with the given value.
    - calcule_monetary_correction(self): Calculates the monetary correction for the statement if it exists.
    - get_corrected_value(self) -> float: Retrieves the corrected value of the statement if the monetary correction
      exists, or else returns 0.

    Note:
    The 'calcule_monetary_correction()' method uses the '_get_monetary_correction()' method, which should be defined
    in the class that inherits or implements the 'AbstractStatement' class.
    """

    class Meta:
        verbose_name = _('Statement Fund')
        verbose_name_plural = _('Statement Funds')

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """
        Save the instance of AbstractStatementFunds and calculate its dtt value
        Calculates the value of dtt using the get_dtt_value() method.
        """
        super(StatementFunds, self).save(*args, **kwargs)
        if send_signal_post_save:
            gen_statement_funds.send(sender=self.__class__, instance=self)

    def has_monetary_correction(self) -> bool:
        """Returns True if the monetary correction exists for the statement."""
        return hasattr(self, 'monetarycorrection')

    def _set_status(self, value: str):
        """Sets the status of the statement with the given value."""
        self._check_status_choice(value)
        self.status = value
        self.save(send_signal_post_save=False)

    def calcule_monetary_correction(self):
        """Retrieves the corrected value of the statement if the monetary correction exists, or else returns 0."""
        data = self._get_monetary_correction()
        if data:
            if self.has_monetary_correction():
                self.monetarycorrection.dict_update(data)
            else:
                data['statement'] = self
                MonetaryCorrection.objects.get_or_create(defaults=data, **{'statement': self})
            self.set_calculation_done()

    def get_corrected_value(self) -> float:
        """Returns corrected value if the monetary correction exists for the statement, else 0"""
        if self.has_monetary_correction():
            return self.monetarycorrection.corrected_value
        return 0


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
    The 'calcule_monetary_correction()' method uses the '_get_monetary_correction()' method, which should be defined
    in the class that inherits or implements the 'AbstractStatement' class.
    """
    description = models.CharField(_('Descrição da verba'), max_length=150)

    class Meta:
        verbose_name = _('Statement Fund Integration')
        verbose_name_plural = _('Statement Funds Integrations')

    def has_monetary_correction(self) -> bool:
        """Returns True if the monetary correction exists for the statement."""
        return hasattr(self, 'monetarycorrectionintegrations')

    def _set_status(self, value: str):
        """Sets the status of the statement with the given value."""
        self._check_status_choice(value)
        StatementIntegrations.objects.filter(id=self.id).update(status=value)

    def calcule_monetary_correction(self):
        """Retrieves the corrected value of the statement if the monetary correction exists, or else returns 0."""
        data = self._get_monetary_correction()
        if data:
            if self.has_monetary_correction():
                self.monetarycorrectionintegrations.dict_update(data)
            else:
                data['statement'] = self
                MonetaryCorrectionIntegrations.objects.get_or_create(defaults=data, **{'statement': self})
            self.set_calculation_done()

    def get_corrected_value(self) -> float:
        """Returns corrected value if the monetary correction exists for the statement, else 0"""
        if self.has_monetary_correction():
            return self.monetarycorrectionintegrations.corrected_value
        return 0


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
    fund = models.ForeignKey(Funds, on_delete=models.PROTECT)
    fund_name = models.CharField(_('Verbas'), max_length=150)
    taxable_amounts = models.FloatField(_('Valores tributáveis'))

    class Meta:
        verbose_name = _('Statement IRRF')
        verbose_name_plural = _('Statement IRRFs')


class StatementDocuments(AbstractStatement):
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
    This class does not define any methods.
    """
    number = models.CharField(_('Número do documento'), max_length=100)
    data_base = models.DateField('Data base')
    historical_value = models.FloatField(_('Valor histórico'))
    fund = models.OneToOneField(Funds, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.data_base} - {self.historical_value}'

    class Meta:
        verbose_name = _('Statement Document')
        verbose_name_plural = _('Statement Documents')


class AbstractMonetaryCorrection(AbstractModel):
    """
    The AbstractMonetaryCorrection class is an abstract base class that defines the common attributes and methods for
    monetary corrections.

    Attributes:
        index_data_base (float): The index value at the reference date for the correction.
        index_recovering (float): The index value at the recovery date for the correction.
        corrected_value (float): The corrected value obtained by applying the correction factors.
    Methods:
        __get_statement: Return statement object associated with the current fund object
        """
    index_data_base = models.FloatField(_('Índice na Data base'))
    index_recovering = models.FloatField(_('Índice na recuperação'))

    def __get_statement(self):
        """
        This method returns the statement object associated with the current fund object. If the
        object does not exist, it raize implemented error.
        """
        if hasattr(self, 'statement') is False or self.statement is None:
            raise NotImplementedError('Necessário o relacionamento OneToOneField para o StatementFunds')
        return self.statement

    @property
    def corrected_value(self) -> float:
        """Returns corrected value calculated"""
        historical_value = self.__get_statement().historical_value
        corrected_value = self.index_recovering / self.index_data_base * historical_value if historical_value > 0 else 0
        return corrected_value

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.index_data_base} - {self.index_recovering} - {self.corrected_value}'


class MonetaryCorrection(AbstractMonetaryCorrection):
    """
    A class that represents a monetary correction for a statement of funds.

    In <Excel>, it refers to each piece of data that can be inserted in the table of funds, monetary correction in the
    rates sheets (tst, moral damages, etc.)

    Attributes:
    statement (StatementFunds): The statement of funds to which the monetary correction applies.
    """
    statement = models.OneToOneField(StatementFunds, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Monetary Correction')
        verbose_name_plural = _('Monetary Corrections')


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

    class Meta:
        verbose_name = _('Monetary Correction Integration')
        verbose_name_plural = _('Monetary Corrections Integrations')


class MonetaryCorrectionDocuments(AbstractMonetaryCorrection):
    """
    A class that represents a monetary correction for a statement of integrations.

    In <Excel>, it refers to each piece of data that can be inserted in the document table on the accounting statement
    sheets (document)

    Attributes:
    statement (StatementIntegrations): The statement of integrations to which the monetary correction applies.
    """
    statement = models.OneToOneField(
        StatementDocuments, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Monetary Correction Document')
        verbose_name_plural = _('Monetary Corrections Documents')


class ArrearsCharges(AbstractModel):  # Encargos moratórios
    """
    A class that represents a monetary correction for a statement of integrations.

    In <Excel>, it refers to each data that can be inserted in the documents table in the extract accounting sheets

    Attributes:
    statement (StatementIntegrations): The statement of integrations to which the monetary correction applies.
    """
    statement = models.OneToOneField(
        StatementDocuments, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Arrears Charge')
        verbose_name_plural = _('Arrears Charges')


class AbstractValue(AbstractModel):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. This class is meant to be
    subclassed to create specific value types associated with a StatementPF object, such as TaxDays,
    RecurralDeposit, DefaultInterest, DefaultInterestDue, TotalDue, and TotalLawyer. The abstract flag
    in the Meta class indicates that this model should not be instantiated directly.
    """
    value = models.FloatField(_('Valor'))
    arrears_charges = models.OneToOneField(
        ArrearsCharges, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class Days(AbstractValue):
    """
    Defines an abstract model for a value associated with a ArrearsCharges object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a ArrearsCharges object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """

    class Meta:
        verbose_name = _('Day')
        verbose_name_plural = _('Days')


class Interest(AbstractValue):  # Juros
    """
    Defines an abstract model for a value associated with a ArrearsCharges object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a ArrearsCharges object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """

    class Meta:
        verbose_name = _('Interest')
        verbose_name_plural = _('Interests')


class Fine(AbstractValue):
    """
    Defines an abstract model for a value associated with a ArrearsCharges object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a ArrearsCharges object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """

    class Meta:
        verbose_name = _('Fine')
        verbose_name_plural = _('Fines')


class AmountDue(AbstractModel):
    """
    Defines an abstract model for a value associated with a StatementDocuments object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementDocuments object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    value = models.FloatField(_('Valor'))
    statement_document = models.OneToOneField(
        StatementDocuments, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Amount Due')
        verbose_name_plural = _('Amount Dues')


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
    fund = models.OneToOneField(Funds, on_delete=models.PROTECT)

    # TODO: somar todas as StatementIRRF. Calcular no evento signals.post.save ou em Procedure
    total = models.FloatField('Total da soma dos valores', default=0)

    def __str__(self):
        return f'{self.fund} - {self.taxable_amount}'

    class Meta:
        verbose_name = _('Total value')
        verbose_name_plural = _('Total values')


class AbstractTotalValuesFunds(AbstractModel):
    """
    A class that represents the total values of a fund, which is an abstract model.

    Attributes:
    total_historical (float): The historical value of the fund.
    total_corrected (float): The corrected value of the fund.
    fund (Funds): The fund to which the values apply.
    """
    fund = models.OneToOneField(Funds, on_delete=models.PROTECT)

    # TODO: somar todas as StatementFunds or StatementFundsIntegrations. Calcular no evento signals.post.save
    total_historical = models.FloatField(_('Total valor histórico'), default=0)
    total_corrected = models.FloatField(_('Total valor corrigido'), default=0)

    def __str__(self):
        return f'{self.fund} - {self.total_historical} - {self.total_corrected}'

    class Meta:
        abstract = True


class TotalValuesFunds(AbstractTotalValuesFunds):
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
        for statement in statements:
            total_corrected_value += statement.get_corrected_value()
            total_historical_value += statement.get_historical_value()
        self.total_historical = total_corrected_value
        self.total_corrected = total_historical_value
        self.save()

    class Meta:
        verbose_name = _('Total value fund')
        verbose_name_plural = _('Total values funds')


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
            total_historical_value += statement.get_historical_value()
        self.total_historical = total_corrected_value
        self.total_corrected = total_historical_value
        self.save()

    class Meta:
        verbose_name = _('Total value fund integration')
        verbose_name_plural = _('Total values funds integrations')


@receiver(gen_statement_funds, sender=StatementFunds)
def get_save_rate(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementFunds object is saved. It
    calculates the monetary correction for the instance and generates the total statements of the related fund. It
    takes the sender and instance as arguments
    """
    print('Signal gerar linha extrato verbas\n')

    instance.calcule_monetary_correction()
    instance.fund.gen_total_statements()
    return


@receiver(gen_total_funds, sender=Funds)
def get_save_rate(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementFunds object is saved. It
    calculates the monetary correction for the instance and generates the total statements of the related fund. It
    takes the sender and instance as arguments
    """
    print('Signal somar todas as linhas de extrato verbas\n\n')
    instance.gen_total_statements()
    instance.gen_total_integrations()


@receiver(post_save, sender=StatementIntegrations)
def get_save_rate_integrations(sender, instance, **kwargs) -> None:
    """
    This method is a receiver for post_save signal and is triggered when a StatementIntegrations object is saved. It
    calculates the monetary correction for the instance and generates the total integrations of the related fund. It
    takes the sender and instance as arguments
    """
    instance.calcule_monetary_correction()


# class Template(AbstractModel):
#     fund_name = models.CharField(_('Verbas'), max_length=150)
#
#
# class TemplateFields(AbstractModel):
#     fund_name = models.CharField(_('Nome do campo'), max_length=150)
#     is_editable = models.BooleanField(_('É editavel?'))
#     fund = models.ForeignKey(Template, on_delete=models.PROTECT)
#
#
# json = {
#     'nome_da_Verba': 'tst - reflexos',
#     'campos': [
#         {
#             'key': 'campo1_data_base',
#             'label': 'campo1_data_base',
#             'e_editavel': True,
#             'tipo_de_input': 'date',
#             'order_by': 1,
#         },  {
#             'key': 'campo1_valor_historico',
#             'label': 'Valor historico',
#             'e_editavel': True,
#             'tipo_de_input': 'date',
#             'order_by': 2,
#         },  {
#             'key': 'campo1_indice',
#             'label': 'Indice',
#             'e_editavel': False,
#             'tipo_de_input': 'float',
#         }
#     ]
# }