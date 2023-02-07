from django.db import models
from creditors.models import Creditor
from projects.abstract_project.models import AbstractCredit
# from projects.project.models import Project
# from creditors.classes.models import Classes
# from creditors.coins.models import Coins
# from core.abstract.models import AbstractModel


class Notice(AbstractCredit): # Edital
    client = models.OneToOneField(Creditor, on_delete=models.PROTECT)
    # classes = models.ForeignKey(Classes, on_delete=models.PROTECT)
    # coins = models.ForeignKey(Coins, on_delete=models.PROTECT)
    # archive_json = models.TextField(blank=True)

    # def __str__(self):
    #     return f"{self.id} | {str(self.creditor)}"
