"""
Defines models for financial statements and funds.

AbstractModel is inherited for common fields such as id, created_at, and updated_at.
Funds class is used to represent a financial fund with a name and calculation.
AbstractStatement class is an abstract model used to represent a financial statement,
with fields for a data base date, historical value, and a foreign key to Funds.
StatementFunds class extends AbstractStatement to represent a statement related to funds.
StatementIntegrations extends AbstractStatement and includes a description field.
"""

from django.db import models
from calculation.models import Calculation
from core.abstract.models import AbstractModel


class Funds(AbstractModel):
    """
    A model class that represents Funds.

    This class inherits from the AbstractModel class and represents a fund with a name and a foreign key relationship to a Calculation object. The 'name' attribute is a character field with a maximum length of 50, and represents the name of the fund. The 'calculation' attribute is a foreign key relationship to a Calculation object and ensures that the relationship is protected upon deletion.

    Attributes:
    name (CharField): Represents the name of the fund.
    calculation (ForeignKey): Represents a foreign key relationship to a Calculation object.

    Methods:
    This class does not define any methods.
    """

    name = models.CharField('Nome da verba', max_length=50)
    calculation = models.ForeignKey(Calculation, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Fund'
        verbose_name_plural = 'Funds'

    def __str__(self):
        return self.name


class AbstractStatement(AbstractModel):
    """
    A model class that represents an abstract financial statement.

    This class inherits from the AbstractModel class and represents an abstract financial statement with a data base date, historical value, and a foreign key relationship to a Funds object. The 'data_base' attribute is a date field that represents the date of the financial statement. The 'historical_value' attribute is a float field that represents the historical value of the statement. The 'funds' attribute is a foreign key relationship to a Funds object and ensures that the relationship is protected upon deletion.

    Attributes:
    data_base (DateField): Represents the date of the financial statement.
    historical_value (FloatField): Represents the historical value of the statement.
    funds (ForeignKey): Represents a foreign key relationship to a Funds object.

    Methods:
    This class does not define any methods.

    Meta:
    abstract (bool): A boolean flag that indicates that this is an abstract model and should not be used to create database tables.
    """
    data_base = models.DateField('Data base')
    historical_value = models.FloatField('Valor histórico')
    fund = models.ForeignKey(Funds, on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.data_base} - {self.historical_value}'


class StatementFunds(AbstractStatement):
    """
    A model class that represents a financial statement for a fund.

    This class inherits from the AbstractStatement class and represents a financial statement for a fund. It has the same attributes as the AbstractStatement class, which include a data base date, historical value, and a foreign key relationship to a Funds object.

    Attributes:
    This class has the same attributes as the AbstractStatement class.

    Methods:
    This class does not define any methods.
    """


class StatementIntegrations(AbstractStatement):
    """
    A model class that represents a financial statement for an integration.

    This class inherits from the AbstractStatement class and represents a financial statement for an integration. It has the same attributes as the AbstractStatement class, which include a data base date, historical value, and a foreign key relationship to a Funds object. Additionally, it has a 'description' attribute, which is a character field with a maximum length of 150 that represents a description of the integration.

    Attributes:
    This class has the same attributes as the AbstractStatement class, as well as:
    description (CharField): Represents a description of the integration.

    Methods:
    This class does not define any methods.
    """
    description = models.CharField('Descrição da verba', max_length=150)


class StatementIRRF(AbstractModel):
    """
    This class represents a statement of taxable amounts for a given fund, used to calculate the Income Tax Withholding at Source
    (IRRF - Imposto de Renda Retido na Fonte in Portuguese) in Brazil. It is a subclass of AbstractStatement.

    Attributes:
    fund (ForeignKey): The foreign key to the Fund model, representing the fund associated with this statement.
    fund_name (CharField): The name of the fund associated with this statement.
    taxable_amounts (FloatField): The taxable amounts for this statement, used to calculate the IRFF.
    """
    fund = models.ForeignKey(Funds, on_delete=models.PROTECT)
    fund_name = models.CharField('Verbas', max_length=150)
    taxable_amounts = models.FloatField('Valores tributáveis')


class StatementDocuments(AbstractStatement):
    """
    A model class that represents a financial statement for a fund.

    This class inherits from the AbstractStatement class and represents a financial statement for a fund. It has the same attributes as the AbstractStatement class, which include a data base date, historical value, and a foreign key relationship to a Funds object.

    Attributes:
    This class has the same attributes as the AbstractStatement class.

    Methods:
    This class does not define any methods.
    """
    number = models.CharField('Número do documento', max_length=100)
    data_base = models.DateField('Data base')
    historical_value = models.FloatField('Valor histórico')
    fund = models.OneToOneField(Funds, on_delete=models.PROTECT)

    # class Meta:
    #     abstract = True

    def __str__(self):
        return f'{self.data_base} - {self.historical_value}'


class AbstractMonetaryCorrection(AbstractModel):
    """
    The AbstractMonetaryCorrection class is an abstract base class that defines the common attributes and methods for monetary corrections.

    Attributes:

    index_data_base (float): The index value at the reference date for the correction.
    index_recovering (float): The index value at the recovery date for the correction.
    corrected_value (float): The corrected value obtained by applying the correction factors.
    Methods:

    __str__: Returns a string representation of the object.
    The class is not meant to be instantiated directly, but to be subclassed by concrete classes that specify the statement to which the correction applies.
    """
    index_data_base = models.FloatField('Indice na data base')
    index_recovering = models.FloatField('Indice na recuperação')
    corrected_value = models.FloatField('Valor corrigido')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.index_data_base} - {self.index_recovering} - {self.corrected_value}'


class MonetaryCorrection(AbstractMonetaryCorrection):
    """
    A class that represents a monetary correction for a statement of funds.

    Attributes:
    statement (StatementFunds): The statement of funds to which the monetary correction applies.
    """
    statement = models.OneToOneField(StatementFunds, on_delete=models.PROTECT)


class MonetaryCorrectionIntegrations(AbstractMonetaryCorrection):
    """
    A class that represents a monetary correction for a statement of integrations.

    Attributes:
    statement (StatementIntegrations): The statement of integrations to which the monetary correction applies.
    """
    statement = models.OneToOneField(
        StatementIntegrations, on_delete=models.PROTECT)


class MonetaryCorrectionDocuments(AbstractMonetaryCorrection):
    """
    A class that represents a monetary correction for a statement of integrations.

    Attributes:
    statement (StatementIntegrations): The statement of integrations to which the monetary correction applies.
    """
    statement = models.OneToOneField(
        StatementDocuments, on_delete=models.PROTECT)


class ArrearsCharges(AbstractModel):  # Encargos moratórios
    """
    A class that represents a monetary correction for a statement of integrations.

    Attributes:
    statement (StatementIntegrations): The statement of integrations to which the monetary correction applies.
    """
    statement = models.OneToOneField(
        StatementDocuments, on_delete=models.PROTECT)


class AbstractValue(AbstractModel):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. This class is meant to be
    subclassed to create specific value types associated with a StatementPF object, such as TaxDays,
    RecurralDeposit, DefaultInterest, DefaultInterestDue, TotalDue, and TotalLawyer. The abstract flag
    in the Meta class indicates that this model should not be instantiated directly.
    """
    value = models.FloatField('Valor')
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


class Interest(AbstractValue):
    """
    Defines an abstract model for a value associated with a ArrearsCharges object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a ArrearsCharges object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """


class Fine(AbstractValue):
    """
    Defines an abstract model for a value associated with a ArrearsCharges object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a ArrearsCharges object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """


class AmountDue(AbstractModel):
    """
    Defines an abstract model for a value associated with a StatementDocuments object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementDocuments object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    value = models.FloatField('Valor')
    statement_document = models.OneToOneField(
        StatementDocuments, on_delete=models.PROTECT)


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
    taxable_amount = models.FloatField('Valor tributável', default=0)
    months_period = models.PositiveIntegerField('Meses no período')
    taxable_portion = models.FloatField('Parcela tributável', default=0)
    aliquot = models.FloatField('Alíquota', default=0)
    installment_deducted = models.FloatField('Parcela a deduzir', default=0)
    irrf_per_month = models.FloatField('Valor IRRF por mês', default=0)
    irrf_per_period = models.FloatField('Valor do IRRF no período', default=0)
    fund = models.OneToOneField(Funds, on_delete=models.PROTECT)

    # TODO: somar todas as StatementIRRF. Calcular no evento signals.post.save ou em Procedure
    total = models.FloatField('Total da soma dos valores', default=0)

    def __str__(self):
        return f'{self.fund} - {self.taxable_amount}'


class AbstractTotalValuesFunds(AbstractModel):
    """
    A class that represents the total values of a fund, which is an abstract model.

    Attributes:
    total_historical (float): The historical value of the fund.
    total_corrected (float): The corrected value of the fund.
    fund (Funds): The fund to which the values apply.
    """
    fund = models.OneToOneField(Funds, on_delete=models.PROTECT)

    # TODO: somar todas as StatementFunds or StatementFundsIntegrations. Calcular no evento signals.post.save ou em Procedure
    total_historical = models.FloatField('Total valor histórico', default=0)
    total_corrected = models.FloatField('Total valor corrigido', default=0)

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
    """


class TotalValuesFundsIntegrations(AbstractTotalValuesFunds):
    """
    A class that represents the total values of a fund, which is a concrete implementation of AbstractTotalValuesFunds.

    Attributes:
    total_historical (float): The historical value of the fund.
    total_corrected (float): The corrected value of the fund.
    fund (Funds): The fund to which the values apply.
    """
