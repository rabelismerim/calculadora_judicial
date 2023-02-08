from django.db import models
from calculation.models import Calculation
from creditors.claim.models import Claim
from projects.abstract_project.models import AbstractDateCreditor


class Criterion(AbstractDateCreditor):
    calculation = models.OneToOneField(Calculation, on_delete=models.PROTECT)
    claim_credor = models.ForeignKey(
        Claim, on_delete=models.PROTECT, related_name='claim_credor')  # Pegar informações do credor
    claim_lawyer = models.ForeignKey(
        Claim, on_delete=models.PROTECT, related_name='claim_lawyer')  # Pegar informações do credor

    def __str__(self):
        return f"{self.id} | {str(self.calculation)}"
