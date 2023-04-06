from django.utils.translation import gettext_lazy as _
from base.coins.models import Coins
from creditors.classes.models import Classes
from django.db import models
from core.abstract.models import AbstractModel
from rates.models import Rate


class AbstractDescription(AbstractModel):
    description = models.CharField(_('Descrição'), max_length=150)

    class Meta:
        abstract = True

    def __str__(self):
        return self.description


class AbstractInfo(AbstractModel):
    name = models.CharField(_('Descrição'), max_length=150)
    legal_number = models.CharField('CPF/CNPJ', max_length=18, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name} - {self.legal_number}'


CHOICES_OCCURENCE = (
    ('A', _('Ajuizamento da Reclamação Trabalhista')), ('C', _('Citação')), ('S', _('Sentença')), ('O', _('Outro')))


class AbstractDateCreditor(AbstractModel):
    # TODO: Verificar se admissão e demissão podem ser alterados, se não possivel, migrar campos para tabela Creditor
    admission = models.DateTimeField(_("Data de admissão"), blank=True, null=True)
    dismissal = models.DateTimeField(_("Data de demissão"), blank=True, null=True)

    # TODO: Verificar se esses valores são para cada credor ou cada recuperanda
    rate = models.ForeignKey(Rate, on_delete=models.PROTECT)
    default_interest = models.FloatField(_('Juros moratórios'), default=0)
    fine = models.FloatField(_('Multa'), default=0)
    advocative_hours = models.FloatField(_('Honorários advocatícios'), default=0)
    occurrence = models.CharField(_('Ocorrência'), max_length=1, choices=CHOICES_OCCURENCE, default='O')

    class Meta:
        abstract = True

    def __str__(self):
        return f'Admissão: {self.admission} | Demissão: {self.dismissal}'


class AbstractDateRecovering(AbstractModel):
    date_rj_request = models.DateField(_("Data do pedido de RJ"), blank=True, null=True)
    date_rj_filing = models.DateField(_("Data de ajuizamento da RJ"), blank=True, null=True)
    date_citation = models.DateField(_("Data da Citação"), blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'Pedido RJ: {self.date_rj_request} | Ajuizamento RJ: {self.date_rj_filing} | Citação: {self.date_citation}'


class AbstractCredit(AbstractModel):
    classes = models.ForeignKey(Classes, on_delete=models.PROTECT, null=True)
    coins = models.ForeignKey(Coins, on_delete=models.PROTECT, null=True)
    archive_json = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.id} | {str(self.classes)}"
