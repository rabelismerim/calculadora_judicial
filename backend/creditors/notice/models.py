from django.db import models
from projects.project.models import Project
from creditors.classes.models import Classes
from creditors.coins.models import Coins
from core.abstract.models import AbstractModel


class Notice(AbstractModel):
    entity = models.ForeignKey(Project, on_delete=models.PROTECT)
    classes = models.ForeignKey(Classes, on_delete=models.PROTECT)
    coins = models.ForeignKey(Coins, on_delete=models.PROTECT)
    value = models.FloatField()
    archive_json = models.TextField(blank=True) 

    def __str__(self):
        return f"{self.id} | {str(self.entity)}"
    