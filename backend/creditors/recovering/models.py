from django.db import models
from core.abstract.models import AbstractModel
from projects.client.models import Client
from creditors.budgets.models import Budgets
from creditors.coins.models import Coins
from creditors.notice.models import Notice
from creditors.archive.models import Archive


class Recovering(AbstractModel):
    '''Class responsible for the grand project/engagement'''
    registration = models.CharField(max_length=15)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    budget = models.ForeignKey(Budgets, on_delete=models.PROTECT)
    STATUS_CHOICES = (
        ("E","Em Análise"),
        ("C","Concluído"),
        ("A","Em Andamento"),
        ("D","Cancelado")
    )        
    status = models.CharField(max_length=1, verbose_name='Status', choices=STATUS_CHOICES, default='E')
    admission = models.DateTimeField(blank=True, null=True)
    dismissal = models.DateTimeField(blank=True, null=True)
    competence = models.DateTimeField(blank=True, null=True)
    coin = models.ForeignKey(Coins, on_delete=models.PROTECT)
    notice = models.ForeignKey(Notice, on_delete=models.PROTECT)
    archive = models.ForeignKey(Archive, on_delete=models.PROTECT)
    status_support = models.CharField(max_length=2, verbose_name='Status Suporte', choices=STATUS_CHOICES, default='E')   

    def __str__(self):
        return f"{self.registration} | {str(self.client)}"
