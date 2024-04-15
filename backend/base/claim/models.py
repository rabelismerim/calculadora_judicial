from django.db import models
from creditors.models import Creditor

from base.models import AbstractCredit


class ClaimCreditor(AbstractCredit):  # Pleito do credor
    creditor = models.ForeignKey(Creditor, on_delete=models.PROTECT)
    is_admin = models.BooleanField(default=False)


class ClaimLawyer(AbstractCredit):  # Pleito advocatícios
    creditor = models.OneToOneField(Creditor, on_delete=models.PROTECT)


class Claim(AbstractCredit):  # Pleito para crítérios
    pass
