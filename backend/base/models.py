from django.utils.translation import gettext_lazy as _, activate, deactivate
from base.coins.models import Coins
from creditors.classes.models import Classes
from django.db import models
from core.abstract.models import AbstractModel
from rates.models import Rate


class AbstractDescription(AbstractModel):
    description = models.CharField(_('Description'), max_length=150)

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')

    def __str__(self):
        return str(self.description)


class AbstractInfo(AbstractModel):
    name = models.CharField(_('Description'), max_length=150)
    legal_number = models.CharField('CPF/CNPJ', max_length=18, unique=True)

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')

    def __str__(self):
        return f'{self.name} - {self.legal_number}'


CHOICES_OCCURRENCE = (
    ('A', _('Labour Complaint Filing')), ('C', _('Citation')), ('S', _('Judgement')), ('O', _(' Other')))
CHOICES_REPRESENTATION_DOCUMENTATION = (
    ('R', _('Regular')), ('P', _('Pending')), ('I', _('Irregular')), ('A', _('AT')))
SELECT_CHOICES_REPRESENTATION_DOCUMENTATION = (
    (_('regular'), 'R'), (_('pendente'), 'P'), (_('irregular'), 'I'), (_('n/a'), 'A'))
CHOICES_CLAIM_TYPE = (
    ('Q', _('Qualification')), ('D', _('Divergence')), ('E', _('Exclusion')), ('A', _('Agreement')),
    ('O', _('Office Analysis')), ('W', _('Ownership')), ('N', _('AT')))

# Use first letter in portugues of word to get choice
SELECT_CHOICES_CLAIM_TYPE = (
    ('H', 'Q'), ('D', 'D'), ('E', 'E'), ('C', 'A'),
    ('A', 'O'), ('T', 'W'), ('N', 'N'))

"""Credor	Credor - CPF/CNPJ (não colocar pontuação)	Credor - Classe	Credor - Moeda	 Credor - Valor """

NATURES = [
    (_('Extrajudicial enforcement action'), _('Ação de execução de título extrajudicial')),
    (_('Bank contract'), _('Contrato bancário')),
    (_('Miscellaneous contracts'), _('Contratos diversos')),
    (_('Advocative hours'), _('Honorários advocatícios')),
    (_('Invoice'), _('Nota fiscal')),
    (_('Rural producer contract'), _('Contrato de produtor rural')),
    (_('Legal title'), _('Título judicial')),
    (_('Labor'), _('Trabalhista')),
    (_('Labor Union'), _('Trabalhista Sindicato')),
    (_('Promissory note'), _('Nota promissória')),
    (_('AT'), _('N/A')),
]

NATURE_CHOICES = [(nature[0], nature[0]) for nature in NATURES]


class NatureChoice(AbstractDescription):
    pass


class AbstractDateCreditor(AbstractModel):
    # TODO: Verificar se admissão e demissão podem ser alterados, se não possível, migrar campos para tabela Creditor
    admission = models.DateField(_("Admission date"), blank=True, null=True)
    dismissal = models.DateField(_("Resignation date"), blank=True, null=True)
    from datetime import date
    dismissal_teste = models.DateField(_("Resignation date"), blank=True, null=True, default=date.today)

    # TODO: Verificar se esses valores são para cada credor ou cada recuperanda
    default_interest = models.FloatField(_('Default interest'), default=0)
    fine = models.FloatField(_('Fine'), default=0)
    advocative_hours = models.FloatField(_('Advocative hours'), default=0)

    # TODO: remover apos o front ter atualizado os calculos
    occurrence = models.CharField(_('Occurrence'), max_length=1, choices=CHOICES_OCCURRENCE, default='O')
    physical_person = models.BooleanField(_('Are you an individual?'), default=True)
    representation_documentation = models.CharField(_('Representation documentation'), max_length=1,
                                                    choices=CHOICES_REPRESENTATION_DOCUMENTATION, default='R')

    claim_type = models.CharField(_('Type'), max_length=1, choices=CHOICES_CLAIM_TYPE, default='A')
    nature = models.ManyToManyField(NatureChoice, blank=True)

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')

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

    # TODO: remover apos o front ter atualizado os calculos
    date_rj_filing = models.DateField(_("RJ filing date"), blank=True, null=True)
    date_citation = models.DateField(_("Citation Date"), blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')

    def __str__(self):
        return _('Request RJ: {}').format(self.date_rj_request)


class AbstractCredit(AbstractModel):
    classes = models.ForeignKey(Classes, on_delete=models.PROTECT, null=True)
    coins = models.ForeignKey(Coins, on_delete=models.PROTECT, null=True)
    archive_json = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')

    def __str__(self):
        return f"{self.id} | {str(self.classes)}"
