"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""

from django.db import models

from core.abstract.models import AbstractModel
from creditors.models import Creditor

CHOICES_STEP = (('S', 'Solicitado'), ('E', 'Em revisão'), ('C', 'Calculado'),
                ('A', 'Aprovado'), ('R', 'Reprovado'))


class Incident(AbstractModel):
    """Attributes:
    incident_number (models.CharField): The number of incidente.
    """
    number = models.CharField('Número do incidente', max_length=100)


class Calculation(AbstractModel):
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
    incident = models.ForeignKey(
        Incident, on_delete=models.PROTECT, null=True)
    creditor = models.ForeignKey(Creditor, on_delete=models.PROTECT)
    step = models.CharField(
        'Passo do cálculo', max_length=1, choices=CHOICES_STEP, default='S')
    appeal_credit = models.BooleanField(
        'Crédito inteiramente concursal?', default=False)
    appeal_deposit = models.BooleanField(
        'Levantamento de depósito recursal?', default=False)
    has_advocative_hours = models.BooleanField(
        'Há honorários no cálculo homologado?', default=False)
    credit_authorization_date = models.DateField(
        'Data da certidão de habilitação de crédito', null=True, default=None)

    # TODO: definir como @property?
    # True If edital AJ else False
    has_edital = models.BooleanField(
        'Edital art. 7º § 2 - 11.101/2005', default=False)

    def get_rate(self):
        """"Pegar o indice que vai ser utilizado"""
        return self.creditor.rate

    def get_date_rj(self):
        """"Pegar a data da recuperacão judicial"""
        return self.creditor.recovering.project.date_rj_request

    def get_default_interest(self):
        """"Pegar o valor da multa"""
        return self.criterion.default_interest

    def get_fine(self):
        """"Pegar o valor da multa"""
        return self.criterion.fine

    def __str__(self):
        return f'{self.creditor}'
