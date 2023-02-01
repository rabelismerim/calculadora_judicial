from django.db import models
from core.abstract.models import AbstractModel


class Recovering(models.Model):
    '''Class responsible for the grand project/engagement'''
    registration = models.CharField(max_length=15)
    id_client = models.ForeignKey("projects.client", on_delete=models.CASCADE, related_name="Entidade")
    id_budget = models.ForeignKey("creditors.budgets", on_delete=models.CASCADE, related_name="Verba")
    status = (
        ("EA","Em Análise"),
        ("CO","Concluído"),
        ("AN","Em Andamento"),
        ("CA","Cancelado")
    )        
    models.CharField(max_length=2, verbose_name='Status', choices=status)
    admission = models.DateTimeField(blank=True, null=True)
    dismissal = models.DateTimeField(blank=True, null=True)
    competence = models.DateTimeField(blank=True, null=True)
    id_coin = models.IntegerField()
    id_notice = models.IntegerField()
    id_archive = models.IntegerField()
    status_support = (
        ("EA","Em Análise"),
        ("CO","Concluído"),
        ("AN","Em Andamento"),
        ("CA","Cancelado")
    )     
    models.CharField(max_length=2, verbose_name='Status Suporte', choices=status_support)   

    def __str__(self):
        return f"{self.registration} | {str(self.id_client)}"
    