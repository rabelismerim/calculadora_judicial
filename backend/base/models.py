from django.utils.translation import gettext_lazy as _
from base.coins.models import Coins
from creditors.classes.models import Classes
from django.db import models
from core.abstract.models import AbstractModel
from rates.models import Rate


class AbstractDescription(AbstractModel):
    description = models.CharField(_('Description'), max_length=150)

    class Meta:
        abstract = True

    def __str__(self):
        return self.description


class AbstractInfo(AbstractModel):
    name = models.CharField(_('Description'), max_length=150)
    legal_number = models.CharField('CPF/CNPJ', max_length=18, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name} - {self.legal_number}'


CHOICES_OCCURRENCE = (
    ('A', _('Labour Complaint Filing')), ('C', _('Citation')), ('S', _('Judgement')), ('O', _(' Other')))


class AbstractDateCreditor(AbstractModel):
    # TODO: Verificar se admissão e demissão podem ser alterados, se não possível, migrar campos para tabela Creditor
    admission = models.DateField(_("Admission date"), blank=True, null=True)
    dismissal = models.DateField(_("Resignation date"), blank=True, null=True)
    from datetime import date
    dismissal_teste = models.DateField(_("Resignation date"), blank=True, null=True, default=date.today)

    # TODO: Verificar se esses valores são para cada credor ou cada recuperanda
    rate = models.ForeignKey(Rate, on_delete=models.PROTECT)
    default_interest = models.FloatField(_('Default interest'), default=0)
    fine = models.FloatField(_('Fine'), default=0)
    advocative_hours = models.FloatField(_('Advocative hours'), default=0)
    occurrence = models.CharField(_('Occurrence'), max_length=1, choices=CHOICES_OCCURRENCE, default='O')
    physical_person = models.BooleanField(_('Are you an individual?'), default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return _('Admission: {} | Resignation: {}').format(self.admission, self.dismissal)

    def is_citation(self) -> bool:
        """See if the occurrence is of type citation"""
        return self.occurrence == 'C'

    def is_filing(self) -> bool:
        """See if the occurrence is of type filing"""
        return self.occurrence == 'A'


class AbstractDateRecovering(AbstractModel):
    date_rj_request = models.DateField(_("RJ order date"), blank=True, null=True)
    date_rj_filing = models.DateField(_("RJ filing date"), blank=True, null=True)
    date_citation = models.DateField(_("Citation Date"), blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return _('Request RJ: {} | Filing RJ: {} | Citation: {}').format(self.date_rj_request, self.date_rj_filing,
                                                                         self.date_citation)


class AbstractCredit(AbstractModel):
    classes = models.ForeignKey(Classes, on_delete=models.PROTECT, null=True)
    coins = models.ForeignKey(Coins, on_delete=models.PROTECT, null=True)
    archive_json = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.id} | {str(self.classes)}"
