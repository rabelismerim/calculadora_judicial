from django.db import models
from creditors.models import Creditor

from base.models import AbstractCredit


class ClaimCreditor(AbstractCredit):  # Pleito do credor
    creditor = models.OneToOneField(Creditor, on_delete=models.PROTECT)


class ClaimLawyer(AbstractCredit):  # Pleito advocaticios
    creditor = models.OneToOneField(Creditor, on_delete=models.PROTECT)


class Claim(AbstractCredit):  # Pleito para críterios
    pass
