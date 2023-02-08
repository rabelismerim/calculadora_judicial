from django.db import models
from core.entity.models import Entity
from projects.abstract_project.models import AbstractDateRecovering
from projects.project.models import Project
from creditors.archive.models import Archive


class Recovering(AbstractDateRecovering):
    '''Class responsible for the grand project/engagement'''
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    process_number = models.CharField("Número do processo", max_length=15)
    STATUS_CHOICES = (
        ("E", "Em Análise"),
        ("C", "Concluído"),
        ("A", "Em Andamento"),
        ("D", "Cancelado")
    )
    status = models.CharField(
        max_length=1, verbose_name='Status', choices=STATUS_CHOICES, default='E')

    competence = models.CharField(
        "Competencia",  max_length=150, null=True, default=None)
    archive = models.ForeignKey(Archive, on_delete=models.PROTECT)
    status_support = models.CharField(
        max_length=2, verbose_name='Status Suporte', choices=STATUS_CHOICES, default='E')

    def __str__(self):
        return f"{self.process_number} | {str(self.client)}"
