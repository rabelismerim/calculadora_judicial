"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from base.models import AbstractCredit
from calculation.comparative.signals import new_calc
from core.abstract.models import AbstractModel
from creditors.models import Creditor
from utils import check_choice

CHOICES_STEP = (
    ('S', _('Requested')), ('C', _('Calculated')), ('E', _('Revised')), ('A', _('Approved')), ('R', _('Failed')),
    ('B', _('Specially Approved')))


class Incident(AbstractModel):
    """Attributes:
    number (models.CharField): The number of incidente.
    """
    number = models.CharField(_('Incident number'), max_length=100)


class Calculation(AbstractCredit):
    """Attributes:
    creditor (models.ForeignKey): The creditor associated with the calculation.
    incident (models.ForeignKey): The incident associated with the calculation.
    step (models.CharField): The step of the calculation (S for survivor or D for deceased).
    appeal_credit (models.BooleanField): Is the credit entirely concursal?
    appeal_deposit (models.BooleanField): Has an appeal deposit been made?
    has_advocative_hours (models.BooleanField): Are there any advocative fees in the homologous calculation?
    credit_authorization_date (models.DateField): The date of the credit authorization certificate.
    has_edital (models.BooleanField): Is there an Article 7 Section 2 - 11.101/2005 Edital?
    """
    incident = models.ForeignKey(Incident, on_delete=models.PROTECT, null=True)
    creditor = models.ForeignKey(Creditor, on_delete=models.PROTECT)
    step = models.CharField(_('Calculation step'), max_length=1, choices=CHOICES_STEP, default='S')
    appeal_credit = models.BooleanField(_('Fully competitive credit?'), default=False)
    appeal_deposit = models.BooleanField(_('Recursal deposit withdrawal?'), default=False)
    has_advocative_hours = models.BooleanField(_('Are there fees in the approved calculation?'), default=False)
    credit_authorization_date = models.DateField(_('Date of credit qualification certificate'), null=True, default=None)

    # TODO: definir como @property?
    # True If edital AJ else False
    has_edital = models.BooleanField(_('Edital art. 7º § 2 - 11.101/2005'), default=False)
    number = models.CharField(_('Calculation number'), max_length=10, null=True, blank=True, default=None)
    recurral_deposit = models.FloatField(_('Recurral deposit released'), default=0)

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

    def get_rate(self):
        """"Pegar o indice que vai ser utilizado"""
        return self.criterion.rate

    def get_date_rj(self):
        """"Pegar a data da recuperacão judicial"""
        return self.criterion.date_rj_request

    def get_default_interest(self):
        """"Pegar o valor da multa"""
        return self.criterion.default_interest

    def get_fine(self):
        """"Pegar o valor da multa"""
        return self.criterion.fine

    def get_appeal_deposit(self):
        """"Pegar se é Levantamento de depósito recursal"""
        return self.appeal_deposit

    def get_lawyer(self):
        """"Pegar o nome do advogado"""
        return self.creditor.recovering.project.lawyer.description

    def set_step_by_char(self, char: str):
        """"Pegar o valor da multa"""
        check_choice(char, CHOICES_STEP)
        self.step = char
        self.save()
