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
from django.utils.translation import gettext_lazy as _

from calculation.models import Calculation
from core.abstract.models import AbstractModel
from dateutil.relativedelta import relativedelta


class AbstractFunds(AbstractModel):
    """
    A model class that represents Funds.

    This class inherits from the AbstractModel class and represents a fund with a name and a foreign key relationship
    to a Calculation object. The 'name' attribute is a character field with a maximum length of 50, and represents
    the name of the fund. The 'calculation' attribute is a foreign key relationship to a Calculation object and
    ensures that the relationship is protected upon deletion.

    In <<Excel>>, it refers to the budget sheets (tst, irrf, moral damages, etc.)

    Attributes:
        name (CharField): Represents the name of the fund. calculation (ForeignKey): Represents a foreign key
        relationship to a Calculation object.

    Methods:
        This class does not define any methods.
    """

    name = models.CharField(_('Fund name'), max_length=50)
    calculation = models.ForeignKey(Calculation, on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


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
        - `_get_index_monetary_correction()` returns the monetary correction based on `data_base`, `date_rj`, and
            `rate` fields.
        - `get_data_base()` returns the `data_base` attribute with or without a summary applied.
        - `get_total_value()` returns the `historical_value` attribute value.
    """
    data_base = models.DateField('Data base')
    historical_value = models.FloatField(_('Valor histórico'))

    # Sumula 381 se refere a cálculos trabalhistas em que o pagamento de salário se dá no mês subsequente ao trabalhado.
    # Sendo necessário adicionar um mês na hora de calcular o valor
    # TODO: Verificar automaticamente se é ou não verba para aplicar a sumula
    fund = models.ForeignKey('funds.Funds', on_delete=models.PROTECT)
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
        """Sets the status of the statement with the given value."""
        self._check_status_choice(value)
        self.status = value
        self.save(send_signal_post_save=False)

    def _get_index_monetary_correction(self) -> dict or None:
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
        if hasattr(self, 'summary') and self.summary:
            return self.data_base + relativedelta(months=1)
        return self.data_base

    def get_total_value(self) -> FloatField:
        """Returns the `historical_value` attribute value"""
        return self.historical_value

    def get_historical_value(self) -> FloatField:
        """Returns the `historical_value` attribute value"""
        return self.historical_value

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.data_base} - {self.historical_value}'


class AbstractMonetaryCorrection(AbstractModel):
    """
    The AbstractMonetaryCorrection class is an abstract base class that defines the common attributes and methods for
    monetary corrections.

    Attributes:
        index_data_base (float): The index value at the reference date for the correction.
        index_recovering (float): The index value at the recovery date for the correction.
        corrected_value (float): The corrected value obtained by applying the correction factors.
    Methods:
        _get_statement: Return statement object associated with the current fund object
        """
    index_data_base = models.FloatField(_('Índice na Data base'))
    index_recovering = models.FloatField(_('Índice na recuperação'))

    def _get_statement(self):
        """
        This method returns the statement object associated with the current fund object. If the
        object does not exist, it raize implemented error.
        """
        if hasattr(self, 'statement') is False or self.statement is None:
            raise NotImplementedError('Necessário o relacionamento OneToOneField para o Statement')
        return self.statement

    @staticmethod
    def _calc_corrected_value(index_recovering, index_data_base, total_value) -> float:
        return index_recovering / index_data_base * total_value

    @property
    def corrected_value(self) -> float:
        """Returns corrected value calculated"""
        total_value = self._get_statement().get_total_value()
        if total_value == 0:
            return 0
        return self._calc_corrected_value(self.index_recovering, self.index_data_base, total_value)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.index_data_base} - {self.index_recovering} - {self.corrected_value}'


class AbstractTotalValuesFunds(AbstractModel):
    """
    A class that represents the total values of a fund, which is an abstract model.

    Attributes:
        total_historical (float): The historical value of the fund.
        total_corrected (float): The corrected value of the fund.
        fund (Funds): The fund to which the values apply.
    """

    # TODO: somar todas as StatementFunds or StatementFundsIntegrations. Calcular no evento signals.post.save
    total_historical = models.FloatField(_('Total valor histórico'), default=0)
    total_corrected = models.FloatField(_('Total valor corrigido'), default=0)

    def __str__(self):
        return f'{self.total_historical} - {self.total_corrected}'

    class Meta:
        abstract = True
