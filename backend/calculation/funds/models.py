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


# class StatementIRFF(AbstractStatement):
#     """
#     A model class that represents a financial statement for an integration.

#     This class inherits from the AbstractStatement class and represents a financial statement for an integration. It has the same attributes as the AbstractStatement class, which include a data base date, historical value, and a foreign key relationship to a Funds object. Additionally, it has a 'description' attribute, which is a character field with a maximum length of 150 that represents a description of the integration.

#     Attributes:
#     This class has the same attributes as the AbstractStatement class, as well as:
#     description (CharField): Represents a description of the integration.

#     Methods:
#     This class does not define any methods.
#     """
#     fund = models.CharField('Verbas', max_length=150)
#     taxable_amounts = models.FloatField('Valores tributáveis')
