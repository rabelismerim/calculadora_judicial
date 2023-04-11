"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
import datetime
import time

import django.db.utils
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from calculation.comparative.signals import new_calc
from calculation.funds.abstract.models import AbstractStatus
from calculation.funds.integrations.models import TotalValuesFundsIntegrations
from calculation.funds.models import TotalValuesFunds
from calculation.models import Calculation
from calculation.statement.models import Statement
from core.abstract.models import AbstractModel
from utils import days360

CHOICES_TOTAL_PF = (('A', 'Total atualizado'), ('D', 'Total devido'))
CHOICES_TAX_DAYS = (('T', 'Taxa SELIC no período'), ('D', 'Dias em atraso'))
CHOICES_DEFAULT_INTEREST_DUE = (('T', 'Total após juros de mora'), ('D', 'Total devido'))


class StatementPF(AbstractStatus):
    """
    Defines a model for a total value associated with a statement. Inherits from the AbstractModel class,
    which provides common fields such as id, created_at, and updated_at. Contains fields for a field
    description and a total value, as well as a OneToOneField to a Statement object. Subclass this model
    to add specific fields as needed and calculate the total value in the post-save event or a Procedure.
    Attributes:
        description: A field for a statement's field description.
        total: A field for the total value.
        statement: A OneToOneField to a Statement object.

    Methods:
        get_recurral_deposit: Returns the recurral deposit for a statement.
        get_default_interest: Returns the default interest value.
        get_default_interest_due: Returns the default interest due.
        _get_calculate_total_value: Calculates the total value.
        _get_date_rj_filing: Returns the date of RJ filing.
        _get_date_rj_request: Returns the date of an RJ request.
        _set_total: Sets the total value.
        _get_total: Returns the total value.
        total_due: Calculates the total due.
        _get_creditor_default_interest: Returns the default interest of a creditor.
        _calcule_set_description: Calculates the description.
        calcule_total: Calculates the total value for a statement.
        _get_taxdays_value: Gets the number of tax days.
        _get_defaultinterest_value: Gets the default interest value.
        _get_rate: Gets the rate.
        total_conclusion: Calculates the total conclusion.
        _has_tax: Determines if a statement has tax.
        _get_appeal_deposit: Gets the appeal deposit for a statement.
        _calcule_get_description: Calculates the description for a statement.
        _calcule_get_tax_days_description: Calculates the tax day description.
        _calcule_get_tax_days_value: Calculates the tax day value.
        _calcule_set_tax_days: Calculates the tax days.
        _delete_tax_days: Deletes tax days.
        _delete_default_interest_due: Deletes the default interest due.
        _calcule_has_default_interest: Determines if a statement has default interest.
        _calcule_default_interest: Calculates the default interest for a statement.
        _delete_default_interest: Deletes the default interest.
        _calcule_set_default_interest: Calculates the default interest.
        _calcule_default_interest_due_value: Calculates the default interest due value.
        _calcule_get_default_interest_due_description: Calculates the default interest due description.
        _calcule_set_default_interest_due: Calculates the default interest due.
        save: Overrides the base class's save method to carry out additional calculations and set the status of the
        statement.
    """
    description = models.CharField('Legenda', max_length=1, choices=CHOICES_TOTAL_PF, default='A')
    total = models.FloatField('Valor total', default=0)
    statement = models.OneToOneField(Statement, on_delete=models.PROTECT)

    def get_recurral_deposit(self) -> float:
        """
        Get the amount of the recurral deposit.
        :returns: float - the amount of the recurral deposit
        """
        return self.statement.calculation.recurral_deposit

    def get_default_interest(self) -> float:
        """Returns the value of the default interest due if it exists, otherwise returns None"""
        if hasattr(self, 'defaultinterest'):
            return self.defaultinterest.value
        return 0

    def get_default_interest_due(self) -> float or None:
        """
        Excel C38
        Returns the value of the default interest due if it exists, otherwise returns None
        """
        if hasattr(self, 'defaultinterestdue'):
            return self.defaultinterestdue.value
        return None

    def _get_calculate_total_value(self) -> float:
        """
        Calculates and returns the total value by summing the
        'total' field of all 'FundsDescription' objects
        """
        return sum(fd.total for fd in self.fundsdescription_set.all())

    def _get_date_rj_filing(self) -> datetime.date or None:  # B19
        """
        Excel B19

        =IF('Ficha de Análise'!$F$66='citação';'Ficha de Análise'!D64;'Ficha de Análise'!D63)
        Returns the 'date_rj_filing' value from criteria if occurrence is 'C',
        otherwise returns the 'date_citation' value from criteria

        If either date_rj_filing or date_citation does not exist, sets an error value and returns None
        """
        if self.statement.calculation.criterion.occurrence == 'C':
            date_citation = self.statement.calculation.criterion.date_citation
        else:
            date_citation = self.statement.calculation.criterion.date_rj_filing
        if not date_citation:
            self.set_error_citation()
        return date_citation

    def _get_date_rj_request(self) -> datetime.date or None:  # B18
        """
            Excel B18

            Returns 'date_rj_request' from statement criteria
            If date_rj_request does not exist, sets an error value and returns None
        """
        date_rj_request = self.statement.calculation.criterion.date_rj_request
        if not date_rj_request:
            self.set_error_rj()
        return date_rj_request

    def _set_total(self):
        """
        Calculates and sets the 'total' field by calling '_get_calculate_total_value()'
        """

        self.total = self._get_calculate_total_value()

    def _get_total(self):
        """
        Excel C35

        Returns the 'total' field
        """
        return self.total

    @property
    def total_due(self) -> float or None:
        """
        Excel C40

        =IF(A40="EXCLUIR LINHA";"N/A";IF($B$19>=$B$18;SUM(C39;C35);SUM(C38:C39)))

        Calculates and returns the total due

        If 'appeal_deposit' is True, adds the 'recurral_deposit' value to 'total'

        If 'date_rj_filing' is greater than or equal to 'date_rj_request',
        returns the sum of 'total' and 'recurral_deposit'

        If 'default_interest_due' exists, returns the sum of 'default_interest_due' and 'recurral_deposit'

        Otherwise, returns 'recurral_deposit'

        If either 'date_rj_filing' or ' date_rj_request' does not exist, returns None
        """
        if self._get_appeal_deposit():
            date_rj_filing = self._get_date_rj_filing()
            date_rj_request = self._get_date_rj_request()
            recurral_deposit = self.get_recurral_deposit()
            if not date_rj_filing or not date_rj_request:
                return None
            if date_rj_filing >= date_rj_request:
                return self._get_total() + recurral_deposit
            if self.get_default_interest_due():
                return self.get_default_interest_due() + recurral_deposit
            return recurral_deposit

    def _get_creditor_default_interest(self) -> float:
        """
        Returns the 'default_interest' value from criteria
        """
        return self.statement.calculation.criterion.default_interest

    def _calcule_set_description(self):
        """
        Sets the 'description' field by calling '_calcule_get_description()'
        """
        self.description = self._calcule_get_description()

    def calcule_total(self):
        """
        Saves the object and calls '_set_total()', '_calcule_set_description()',
        '_calcule_set_tax_days()', '_calcule_set_default_interest()',
        and '_calcule_set_default_interest_due()'
        """
        self.save()

    def _get_taxdays_value(self) -> float:
        """
        Returns the value of 'taxdays' if it exists, otherwise returns 0
        """
        if hasattr(self, 'taxdays'):
            return self.taxdays.value
        return 0

    def _get_defaultinterest_value(self) -> float:
        """
        Returns the value of 'defaultinterest' if it exists, otherwise returns 0
        """
        if hasattr(self, 'defaultinterest'):
            return self.defaultinterest.value
        return 0

    def _get_rate(self):
        """
        Returns the rate from the criteria
        """
        return self.statement.calculation.criterion.rate

    @property
    def total_conclusion(self) -> float or None:
        """
        =IF(N7="Sim";C40;IF($B$19<$B$18;IFERROR(C38;C36);IF($B$19>=$B$18;IFERROR($C$40;$C$35))))

        Calculates and returns the total conclusion

        If 'appeal_deposit' is True, returns 'total_due'

        If 'date_rj_filing' is less than 'date_rj_request' and 'default_interest_due' exists,
        returns the amount of default interest due

        If 'date_rj_filing' is less than 'date_rj_request',
        returns the value calculated by '_get_taxdays_value()'

        If 'date_rj_filing' is greater than or equal to 'date_rj_request' and 'default_interest_due' exists,
        returns the amount of default interest due

        If 'date_rj_filing' is greater than or equal to 'date_rj_request',
        returns the value of 'total'

        If either 'date_rj_filing' or ' date_rj_request' does not exist, returns None
        """
        appeal_deposit = self._get_appeal_deposit()
        date_rj_filing = self._get_date_rj_filing()
        date_rj_request = self._get_date_rj_request()
        default_interest_due = self.get_default_interest_due()
        if not date_rj_filing or not date_rj_request:
            return None
        if appeal_deposit:
            result = self.total_due
        elif date_rj_filing < date_rj_request:
            if default_interest_due:
                result = default_interest_due
            else:
                result = self._get_taxdays_value()
        else:
            if default_interest_due:
                result = default_interest_due
            else:
                result = self._get_total()
        return result

    def _has_tax(self) -> bool:
        """
        self.B19 >= self.B18 or self.B19 == 0
        Calcule if not date_rj_filing or date_rj_filing >= date_rj_request

        Determines whether taxes should be calculated based on 'date_rj_filing' and 'date_rj_request'

        Returns False and sets the excluded line error value if either date does not exist
        Returns True otherwise
        """
        date_rj_filing = self._get_date_rj_filing()
        date_rj_request = self._get_date_rj_request()
        if not date_rj_filing or (date_rj_filing >= date_rj_request):
            return False  # EXCLUIR LINHA
        return True

    def _get_appeal_deposit(self):
        """
        Excel N7

        Returns the value of 'appeal_deposit' from the statement calculation
        """
        return self.statement.calculation.get_appeal_deposit()

    def _calcule_get_description(self) -> str:
        """
        =IF(OR(AND($B$19<$B$18;B19<>0);$N$7="Sim");"Total atualizado";"Total devido")

        Determines and returns the description based on the values of 'date_rj_filing', 'date_rj_request',
        and 'appeal_deposit'
        """
        date_rj_filing = self._get_date_rj_filing()
        date_rj_request = self._get_date_rj_request()
        appeal_deposit = self._get_appeal_deposit()
        if (date_rj_filing and date_rj_filing < date_rj_request) or appeal_deposit:
            return 'A'  # Total atualizado
        return 'D'  # Total devido

    def _calcule_get_tax_days_description(self) -> str or None:
        """
        =IF('Ficha de Análise'!D65="IPCA-E/SELIC";"Taxa SELIC no período";IF(OR($B$19>=$B$18;$B$19=0);"EXCLUIR
        LINHA";"Dias em atraso"))

        Determines and returns the tax days description based on the value of the rate
        """
        rate = self._get_rate()
        if rate.is_ipca_e_selic():
            return 'T'  # Taxa SELIC no período
        elif not self._has_tax():
            return None  # EXCLUIR LINHA
        return 'D'  # Dias em atraso

    def _calcule_get_tax_days_value(self) -> float or None:
        """
        =IF($A$36="EXCLUIR LINHA";"N/A";IF('Ficha de Análise'!D65="ipca-E/SELIC";VLOOKUP(DATE(YEAR('Extrato
        Contábil'!$B$18);MONTH('Extrato Contábil'!$B$18);1);SELIC!A:D;4;FALSE)/VLOOKUP(DATE(YEAR('Extrato
        Contábil'!B19);MONTH('Extrato Contábil'!B19);1);SELIC!A:D;4;FALSE)-1;IF(DAYS360(B19;$B$18)>0;DAYS360(
        B19;$B$18);0)))

        Calculates and returns the tax days value based on the rate, 'date_rj_filing', and 'date_rj_request'
        """
        rate = self._get_rate()
        date_rj_filing = self._get_date_rj_filing()
        date_rj_request = self._get_date_rj_request()
        choice = self._calcule_get_tax_days_description()
        if not choice:
            return None
        elif rate.is_ipca_e_selic():
            """=IF('Ficha de Análise'!D65="ipca-E/SELIC";VLOOKUP(DATE(YEAR('Extrato Contábil'!$B$18);MONTH('Extrato 
            Contábil'!$B$18);1);SELIC!C4!A:D;4;FALSE)/VLOOKUP(DATE(YEAR('Extrato Contábil'!B19);MONTH('Extrato 
            Contábil'!B19);1);SELIC!A:D;4;FALSE)-1 """
            rate_rj_request = rate.get_rate_by_date(date_rj_request)
            rate_rj_filing = rate.get_rate_by_date(date_rj_filing)
            return (rate_rj_request.get_accumulated / rate_rj_filing.get_accumulated - 1) * 100
        return max(0, days360(date_rj_filing, date_rj_request))

    def _calcule_set_tax_days(self):
        """
        Sets the TaxDays object based on the values returned by '_calcule_get_tax_days_description()'
        and '_calcule_get_tax_days_value()''

        If there is no value or no description, deletes the TaxDays object
        """
        choice = self._calcule_get_tax_days_description()
        if not choice:
            self._delete_tax_days()
            return

        value = self._calcule_get_tax_days_value()
        if value is None:
            self._delete_tax_days()
            return
        filters = {'statement_pf_id': self.id}
        default = {'statement_pf_id': self.id, 'description': choice, 'value': value}
        TaxDays.objects.update_or_create(defaults=default, **filters)

    def _delete_tax_days(self):
        """
        Deletes the TaxDays object if it exists
        """
        tax_days = TaxDays.objects.filter(statement_pf_id=self.id).first()
        if tax_days:
            tax_days.delete()

    def _delete_default_interest_due(self):
        """
        Deletes the DefaultInterestDue object if it exists
        """
        default_interest_due = DefaultInterestDue.objects.filter(statement_pf_id=self.id).first()
        if default_interest_due:
            default_interest_due.delete()

    def _calcule_has_default_interest(self) -> bool:
        """
        =IF(OR($B$19>=$B$18;B19=0);"EXCLUIR LINHA";"Juros moratórios")

        Verify if there is default interest to be calculated.

        Returns:
            bool: True, if there is default interest to be calculated; False, otherwise.
        """
        return self._has_tax()

    def _calcule_default_interest(self) -> float:
        """
        IF('Ficha de Análise'!D65="IPCA-E/SELIC";'Extrato Contábil'!C36*'Extrato Contábil'!C35;C35*($B$21/30)*C36)

        Calculate the monetary value of the default interest.

        Returns:
            float: The monetary value of the default interest.
        """
        days_in_arrears = self._get_taxdays_value()
        total = self._get_total()
        creditor_default_interest = self._get_creditor_default_interest()
        rate = self._get_rate()
        if rate.is_ipca_e_selic():
            return days_in_arrears * total / 100
        return (total * (days_in_arrears / 30) * creditor_default_interest) / 100

    def _delete_default_interest(self):
        """Delete the default interest from the database."""
        default = DefaultInterest.objects.filter(statement_pf_id=self.id).first()
        if default:
            default.delete()

    def _calcule_set_default_interest(self):
        """
        =IF(OR($B$19>=$B$18;B19=0);"EXCLUIR LINHA";"Juros moratórios")

        Calculate and save the default interest value in the database.
        """
        if self._calcule_has_default_interest():
            value = self._calcule_default_interest()
            filters = {'statement_pf_id': self.id}
            default = {'statement_pf_id': self.id, 'value': value}
            DefaultInterest.objects.update_or_create(defaults=default, **filters)
        else:
            self._delete_default_interest()

    def _calcule_default_interest_due_value(self) -> float or None:
        """
        =IF($A$38="EXCLUIR LINHA";"N/A";SUM(C37;C35))

        Calculate the total value due, including default interest.

        Returns:
            float or None: The total value due, including default interest, if any; None otherwise.
        """
        if self._calcule_get_default_interest_due_description():
            total = self._get_total()
            default_interest_value = self._get_defaultinterest_value()
            return default_interest_value + total
        return None

    def _calcule_get_default_interest_due_description(self) -> str or None:
        """
        =IF(OR($B$19>=$B$18;B19=0);"EXCLUIR LINHA";IF(AND($B$19<$B$18;$N$7="Sim");"Total após juros de
        mora";"Total devido"))

        Calculate the description of the value due, including default interest.

        Returns:
            str or None: The description of the value due, including default interest, if any; None otherwise.
        """
        date_rj_filing = self._get_date_rj_filing()
        date_rj_request = self._get_date_rj_request()
        appeal_deposit = self._get_appeal_deposit()
        if not self._has_tax():
            return None  # EXCLUIR LINHA
        elif date_rj_filing < date_rj_request and appeal_deposit:
            return 'T'  # Total após juros de mora
        return 'D'  # Total devido

    def _calcule_set_default_interest_due(self):
        """Calculate and save the default interest due value and description in the database."""
        choice = self._calcule_get_default_interest_due_description()
        if not choice:
            self._delete_default_interest_due()
            return

        value = self._calcule_default_interest_due_value()
        if value is None:
            self._delete_default_interest_due()
            return
        filters = {'statement_pf_id': self.id}
        default = {'statement_pf_id': self.id, 'description': choice, 'value': value}
        DefaultInterestDue.objects.update_or_create(defaults=default, **filters)

    def save(self, send_signal_post_save=True, *args, **kwargs):
        """Save the object and perform calculations and updates before saving.

        Args:
            send_signal_post_save (bool): Whether to send a signal after saving the object (default True).
        """
        super(StatementPF, self).save(*args, **kwargs)
        if send_signal_post_save:
            try:
                self.set_in_progress()
                self._set_total()
                self._calcule_set_description()
                self._calcule_set_tax_days()
                self._calcule_set_default_interest()
                self._calcule_set_default_interest_due()
            except TypeError:
                pass
            if not self.total_conclusion:
                self.set_error_parameters()
            else:
                self.set_calculation_done()


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
    statement_pf = models.OneToOneField(StatementPF, on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.value)


class TaxDays(AbstractValue):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    # Taxa SELIC no período, dias em atraso ou EXCLUIR LINHA
    description = models.CharField(_('Legenda'), max_length=1, choices=CHOICES_TAX_DAYS)


class DefaultInterest(AbstractValue):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    # Juros moratórios ou EXCLUIR LINHA


class DefaultInterestDue(AbstractValue):
    """
    Defines an abstract model for a value associated with a StatementPF object. Inherits from the AbstractModel
    class, which provides common fields such as id, created_at, and updated_at. Contains a value field
    for the associated value, as well as a OneToOneField to a StatementPF object. Subclass this model to add
    specific fields as needed and include a field description for the value type.
    """
    # Total após juros de mora, Total devido ou EXCLUIR LINHA
    description = models.CharField('Legenda', max_length=1, choices=CHOICES_DEFAULT_INTEREST_DUE)


class FundsDescription(AbstractModel):
    """
    This class represents a fund description which includes a description field, a value field,
    and a foreign key to the StatementPF model.

    Attributes:
        statement_pf (ForeignKey): a foreign key to the StatementPF model to which the fund description belongs.
        rate (ForeignKey): a foreign key to the TotalValuesFunds model to which the fund description belongs.
        rate_integrations (ForeignKey): a foreign key to the TotalValuesFundsIntegrations model to which the fund
        description belongs.
    """
    statement_pf = models.ForeignKey(StatementPF, on_delete=models.PROTECT)
    rate = models.ForeignKey(TotalValuesFunds, on_delete=models.PROTECT, null=True, blank=True)
    rate_integrations = models.ForeignKey(TotalValuesFundsIntegrations, on_delete=models.PROTECT, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.rate and self.rate_integrations:
            raise AttributeError(_('Não é permitido salvar rate e rate_integrations ao mesmo tempo.'))
        super().save(*args, **kwargs)

    def _get_rate(self):
        """
        Internal method that returns the rate linked to this instance, either the
        self.rate attribute or the self.rate_integrations if the former is None.
        Raises an AttributeError if none of the attributes are set.

        Returns:
            Union[Rate, None]: The Rate instance linked to this object or None
        """
        if self.rate:
            return self.rate
        elif self.rate_integrations:
            return self.rate_integrations
        raise AttributeError('Necessário ter uma verba linkada')

    @property
    def total(self) -> float:
        """
        Property that returns the total corrected value of the rate linked to this instance.

        Returns:
            float: The total corrected value of the Rate instance linked to this object
        """
        return self._get_rate().total_corrected

    @property
    def description(self) -> str:
        """
        Property that returns the description of the rate linked to this instance.

        Returns:
            str: The description of the Rate instance linked to this object
        """
        return self._get_rate().get_description()


def get_create_statement_pf_by_calculation(calculation):
    """
    Returns or creates a StatementPF object related to the given Calculation.

    Parameters:
        calculation (Calculation): Calculation object to get or create a StatementPF for.

    Returns:
        StatementPF: The related StatementPF object.
    """
    statement, created = Statement.objects.get_or_create(calculation_id=calculation.id)
    statement_pf, created = StatementPF.objects.get_or_create(statement_id=statement.id)
    return statement_pf


@receiver(new_calc, sender=Calculation)
def new_calculation(sender, instance, **kwargs) -> None:
    """
    Receives the new_calc signal and creates a StatementPF object for the received Calculation.

    Parameters:
        sender: Sender of the signal.
        instance (Calculation): Calculation object received in the signal.
        kwargs: Additional keyword arguments.

    Returns:
        None.
    """
    print('Signal gerar novo calculo em statement')
    get_create_statement_pf_by_calculation(instance)


@receiver(signals.post_save, sender=TotalValuesFunds)
def new_total_funds_rate(sender, instance, **kwargs) -> None:
    """
    Receives the post_save signal from TotalValuesFunds model and creates a FundsDescription object related to a
    StatementPF object based on the instance's Calculation, and updates the relevant StatementPF total.

    Parameters:
        sender: Sender of the signal.
        instance (TotalValuesFunds): TotalValuesFunds object received in the signal.
        kwargs: Additional keyword arguments.

    Returns:
        None.
    """
    print('Signal total values funds')

    statement_pf = get_create_statement_pf_by_calculation(instance.get_calculation())
    defaults = {'statement_pf_id': statement_pf.id, 'rate_id': instance.id}
    filters = {'statement_pf_id': statement_pf.id}
    FundsDescription.objects.get_or_create(defaults=defaults, **filters)
    statement_pf.calcule_total()


@receiver(signals.post_save, sender=TotalValuesFundsIntegrations)
def new_total_funds_rate_integrations(sender, instance, **kwargs) -> None:
    """
    Receives the post_save signal from TotalValuesFundsIntegrations model and creates a FundsDescription object
    related to a StatementPF object based on the instance's Calculation, and updates the relevant StatementPF total.

    Parameters:
        sender: Sender of the signal.
        instance (TotalValuesFundsIntegrations): TotalValuesFundsIntegrations object received in the signal.
        kwargs: Additional keyword arguments.

    Returns:
        None.
    """
    print('Signal total values funds integrations')
    statement_pf = get_create_statement_pf_by_calculation(instance.get_calculation())
    defaults = {'statement_pf_id': statement_pf.id, 'rate_integrations_id': instance.id}
    filters = {'statement_pf_id': statement_pf.id}
    FundsDescription.objects.get_or_create(defaults=defaults, **filters)
    statement_pf.calcule_total()
