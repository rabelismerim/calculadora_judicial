from django.db import models
from creditors.models import Creditor
from base.models import AbstractCredit


class Notice(AbstractCredit):  # Edital
    client = models.OneToOneField(Creditor, on_delete=models.PROTECT)
