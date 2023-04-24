"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
import datetime

from django.db import models
from django.db.models import Sum, F, BooleanField
from django.utils.translation import gettext_lazy as _

from calculation.comparative.signals import new_calc
from calculation.premise.models import Premise
from core.abstract.models import AbstractModel
from creditors.models import Creditor
from rates.models import Rate
from utils import check_choice

CHOICES_STEP = (
    ('S', _('Requested')), ('C', _('Calculated')), ('E', _('Revised')), ('A', _('Approved')), ('R', _('Failed')),
    ('B', _('Specially Approved')))


class Incident(AbstractModel):
    """
    # Statement A5

    The Incident class is a subclass of the AbstractModel, representing an incident that can occur during the execution
    of a process. It has one attribute:

    Attributes:
        - number (models.CharField): The number of the incident represented as a character field with a maximum length
            of 100.
    """
    # Statement A5
    number = models.CharField(_('Incident number'), max_length=100)


class Calculation(AbstractModel):
    """
    Attributes:
        creditor (models.ForeignKey): The creditor associated with the calculation.
        incident (models.ForeignKey): The incident associated with the calculation.
        step (models.CharField): The step of the calculation (S for survivor or D for deceased).
        appeal_credit (models.BooleanField): Is the credit entirely concursal?
        appeal_deposit (models.BooleanField): Has an appeal deposit been made?
        has_advocative_hours (models.BooleanField): Are there any advocative fees in the homologous calculation?
        date_credit_auth (models.DateField): The date of the credit authorization certificate.
        has_edital (models.BooleanField): Is there an Article 7 Section 2 - 11.101/2005 Edital?
    """
    creditor = models.ForeignKey(Creditor, on_delete=models.PROTECT)
    step = models.CharField(_('Calculation step'), max_length=1, choices=CHOICES_STEP, default='S')
    number = models.CharField(_('Calculation number'), max_length=10, null=True, blank=True)
    recurral_deposit = models.FloatField(_('Recurral deposit released'), default=0)

    # Statement A5
    incident = models.ForeignKey(Incident, on_delete=models.PROTECT, null=True)

    # TODO verificar se essas premissas variam de calculo para calculo, ou pode ser relacionado ao credor
    # Statement N5 - Crédito inteiramente concursal? TODO analisar se as verbas adicionadas são concursal e alterar
    #  automaticamente
    appeal_credit = models.BooleanField(_('Fully competitive credit?'), default=False)
    # Statement Q5 - Data do calculo homologado
    date_approved_calculation = models.DateField(_('Date of credit qualification certificate'), null=True)

    # Statement N7 - Levantamento de depósito recursal?
    appeal_deposit = models.BooleanField(_('Recursal deposit withdrawal?'), default=False)
    # Statement Q7 - Página que mostra o levantamento de depósito recursal
    num_pag_fls_appeal_deposit = models.CharField(_('Page number of the appeal deposit withdrawal'), max_length=10,
                                                  null=True, blank=True)

    # Statement N9 - Data da certidão de habilitação de crédito
    date_credit_auth = models.DateField(_('Date of credit qualification certificate'), null=True)
    # Statement Q9 - Página que mostra o levantamento de depósito recursal
    num_pag_fls_credit_auth_date = models.CharField(_('Calculation number'), max_length=10, null=True, blank=True)
    # Statement N10 - Há honorários advocatícios?
    has_advocative_hours = models.BooleanField(_('Are there fees in the approved calculation?'), default=False)

    # TODO: definir como @property?
    # True If edital AJ else False
    has_edital = models.BooleanField(_('Edital art. 7º § 2 - 11.101/2005'), default=False)
    premises = models.ManyToManyField(Premise, blank=True)

    def _get_number(self) -> str:
        """Returns the number of calculations for the creditor."""
        return f'{self._get_count_process_calculation() + 1} - {self.creditor.get_count_calculations() + 1}'

    def _get_count_process_calculation(self) -> int:
        """Returns the count of Calculation objects for the creditor's project"""
        return Calculation.objects.filter(creditor__recovering__project=self.creditor.recovering.project).exclude(
            number__isnull=True).count()

    def save(self, *args, **kwargs):
        super(Calculation, self).save(*args, **kwargs)
        if not self.id or not self.number:
            self.number = self._get_number()
            if not self.id:
                new_calc.send(sender=self.__class__, instance=self)

    def get_rate(self) -> Rate:
        """
        Excel Analysis sheet B20

        Get rate
        """
        return self.criterion.rate

    def get_date_rj(self) -> datetime.date or None:
        """
        Excel Analysis sheet D66, Statement B18

        Get date RJ request
        """
        return self.criterion.date_rj_request

    def get_default_interest(self) -> float:
        """
        Excel Analysis sheet D66, Statement B21

        Get value of default interest
        """
        return self.criterion.default_interest

    def get_dismissal(self) -> datetime.date or None:
        """
        Excel Analysis sheet D62

        Get dismissal date
        """
        return self.criterion.dismissal

    def get_has_advocative_hours(self) -> bool:
        """
        Excel Statement N10

        Get has advocative hours
        """
        return self.has_advocative_hours

    def get_advocative_hours(self) -> float:
        """
        Excel Analysis sheet D68, Statement B23

        Get value in % of attorney fees
        """
        return self.criterion.advocative_hours

    def get_date_approved_calculation(self) -> datetime.date or None:
        """Get the approved calculation date"""
        # TODO verificar com stakeholders o momento que essa data é recebida, se há alterações ao longo do processo.
        #  Com isso criar o field em calculo, recuperanda ou credor
        return self.date_approved_calculation

    def get_fine(self) -> float:
        """
        Excel Analysis sheet D67, Statement B22

        Get value of fine
        """
        return self.criterion.fine

    def get_appeal_credit(self) -> bool:
        """
        Excel Statement N5

        Get if the credit is entirely bankrupt
        """
        return self.appeal_credit

    def get_appeal_deposit(self) -> bool:
        """
        Excel Statement N7

        Get if it is Recursal deposit withdrawal
        """
        return self.appeal_deposit

    def get_date_credit_auth(self) -> datetime.date or None:
        """
        Excel Statement N9

        Get the date of the credit qualification certificate
        """
        return self.date_credit_auth

    def get_num_pag_fls_appeal_deposit(self) -> str or None:
        """
        Excel Statement Q7

        Get the number of the page that was quoted the withdrawal of the appeal deposit
        """
        return self.num_pag_fls_appeal_deposit

    def get_lawyer(self) -> str:
        """
        Excel Analysis sheet A50

        Get lawyer name
        """
        return self.creditor.recovering.project.lawyer.description

    def set_step_by_char(self, char: str):
        """Set value of current step"""
        check_choice(char, CHOICES_STEP)
        self.step = char
        self.save()

    def get_classes(self) -> list:
        """Groups the Funds, Fund Document and FundIRRF by class and adds the values"""
        classes = list(self.funds_set.all().filter(classes__classe__isnull=False).values(
            classe=F('classes__classe')).distinct().order_by('classes__classe') \
                       .annotate(total_value=Sum('coins__value')))

        classes.extend(
            list(self.funddocument_set.all().filter(classes__classe__isnull=False).values(classe=F('classes__classe'))
                 .distinct().order_by('classes__classe').annotate(total_value=Sum('coins__value'))))

        classes.extend(
            list(self.fundirrf_set.all().filter(classes__classe__isnull=False).values(classe=F('classes__classe'))
                 .distinct().order_by('classes__classe').annotate(total_value=Sum('coins__value'))))

        class_totals = {}
        for class_dict in classes:
            class_name = class_dict['classe']
            class_total = class_dict['total_value']
            if class_name not in class_totals:
                class_totals[class_name] = class_total
            else:
                class_totals[class_name] += class_total

        return [{'classe': class_name, 'total_value': total} for class_name, total in class_totals.items()]

    def get_date_rj_filing(self) -> datetime.date or None:  # B19
        """
        Excel Analysis sheet B19

        =IF('Ficha de Análise'!$F$66='citação';'Ficha de Análise'!D64;'Ficha de Análise'!D63)
        Returns the 'date_rj_filing' value from criteria if occurrence is 'C',
        otherwise returns the 'date_citation' value from criteria

        If either date_rj_filing or date_citation does not exist, sets an error value and returns None
        """
        if self.is_citation():
            date_citation = self.criterion.date_citation
        else:
            date_citation = self.criterion.date_rj_filing
        return date_citation

    def get_date_rj_request(self) -> datetime.date or None:
        """
        Excel Analysis sheet B18

        Returns 'date_rj_request' from statement criteria
        If date_rj_request does not exist, sets an error value and returns None
        """
        return self.criterion.date_rj_request

    def is_citation(self) -> bool:
        """
        Excel analysis sheet C64

        Get if the occurrence in criterion is of type citation
        """
        return self.criterion.is_citation()

    def is_filing(self) -> bool:
        """
        Excel analysis sheet C64

        Get if the occurrence in criterion is of type filing"""
        return self.criterion.is_filing()

    def get_statement(self):
        """
        Gets the statement attribute of the object if it exists.

        Returns:
            - The statement attribute of the object, if it exists.
            - None, otherwise.
        """
        if hasattr(self, 'statement'):
            return self.statement

    def is_agreement(self) -> bool:
        """
        Excel Statement A78

        See if the calculations are for agreements
        """

        # TODO ver se o credor do tipo PF tem acordos feitos
        statement = self.get_statement()
        if statement:
            return True if statement.get_statement_pj() else False
        return False
