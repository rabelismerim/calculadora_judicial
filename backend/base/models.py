from base.coins.models import Coins
from creditors.classes.models import Classes
from django.db import models
from core.abstract.models import AbstractModel
from rates.models import Rate


class AbstractDescription(AbstractModel):
    description = models.CharField('Descrição', max_length=150)

    class Meta:
        abstract = True

    def __str__(self):
        return self.description


class AbstractInfo(AbstractModel):
    # TODO: Criar validador de cpf|cnpj
    name = models.CharField('Descrição', max_length=150)
    legal_number = models.CharField('CPF/CNPJ', max_length=18, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.name} - {self.legal_number}'


class AbstractDateCreditor(AbstractModel):
    # TODO: Verificar se admissão e demissão podem ser alterados, se não possivel, migrar campos para tabela Creditor
    admission = models.DateTimeField("Data de admissão", blank=True, null=True)
    dismissal = models.DateTimeField("Data de demissão", blank=True, null=True)

    # TODO: Verificar se esses valores são para cada credor ou cada recuperanda
    rate = models.ForeignKey(Rate, on_delete=models.PROTECT)
    default_interest = models.FloatField('Juros moratórios', default=0)
    fine = models.FloatField('Multa', default=0)
    advocative_hours = models.FloatField('Honorários advocatícios', default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return f'Admissão: {self.admission} | Demissão: {self.dismissal}'


class AbstractDateRecovering(AbstractModel):
    date_rj_request = models.DateField(
        "Data do pedido de RJ", blank=True, null=True)
    date_rj_filing = models.DateField(
        "Data de ajuizamento da RJ", blank=True, null=True)
    date_citation = models.DateField(
        "Data da Citação", blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'Pedido RJ: {self.date_rj_request} | Ajuizamento RJ: {self.date_rj_filing} | Citação: {self.date_citation}'


class AbstractCredit(AbstractModel):
    classes = models.ForeignKey(Classes, on_delete=models.PROTECT)
    coins = models.ForeignKey(Coins, on_delete=models.PROTECT)
    archive_json = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.id} | {str(self.classes)}"
