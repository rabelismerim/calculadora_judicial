from django.db import models
from core.abstract.models import AbstractModel
from core.entity.models import Entity
from projects.models import Project


class Recovering(AbstractModel):
    '''Class responsible for the grand project/engagement'''
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    STATUS_CHOICES = (
        ("E", "Em Análise"),
        ("C", "Concluído"),
        ("A", "Em Andamento"),
        ("D", "Cancelado")
    )
    status = models.CharField(
        max_length=1, verbose_name='Status', choices=STATUS_CHOICES, default='E')
    status_support = models.CharField(
        max_length=2, verbose_name='Status Suporte', choices=STATUS_CHOICES, default='E')

    def __str__(self):
        return f"{self.project} | {str(self.entity)}"
