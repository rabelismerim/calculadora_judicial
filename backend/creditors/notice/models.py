from django.db import models
from creditors.models import Creditor
from base.models import AbstractCredit


class Notice(AbstractCredit):  # Edital AJ
    creditor = models.OneToOneField(Creditor, on_delete=models.PROTECT)


class NoticeRecovering(AbstractCredit):  # Edital Recuperanda
    creditor = models.OneToOneField(Creditor, on_delete=models.PROTECT)
