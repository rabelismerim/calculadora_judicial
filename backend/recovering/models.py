from django.db import models
from django.utils.translation import gettext_lazy as _
from core.abstract.models import AbstractModel
from core.entity.models import Entity
from projects.models import Project


class Recovering(AbstractModel):
    """Class responsible for the grand project/engagement"""
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    STATUS_CHOICES = (
        ("E", _("Em Análise")),
        ("C", _("Concluído")),
        ("A", _("Em Andamento")),
        ("D", _("Cancelado"))
    )
    status = models.CharField(
        max_length=1, verbose_name='Status', choices=STATUS_CHOICES, default='E')
    status_support = models.CharField(
        max_length=2, verbose_name=_('Status Suporte'), choices=STATUS_CHOICES, default='E')

    def __str__(self):
        return f"{self.project} | {str(self.entity)}"
