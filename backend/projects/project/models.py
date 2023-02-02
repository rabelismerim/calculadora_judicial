from django.db import models
from django.db.models import Count, Min, Sum, Avg
from core.abstract.models import AbstractModel
from core.dttuser.models import User
from projects.judge.models import Judge
from projects.layer.models import Layer
from projects.region.models import Region
from projects.engagement.models import ProjectEngagement
from django.db.models import F


STATUS_CHOICES = (
    ('E', 'Em andamento'),
    ('C', 'Concluido'),
    ('A', 'Em análise'),
    ('F', 'Cancelado'),
)

class Project(AbstractModel):
    '''Class responsible for the grand project/engagement'''

    STATUS_CHOICES = (
        ("E","Em Análise"),
        ("C","Concluído"),
        ("A","Em Andamento"),
        ("D","Cancelado")
    )   

    project_start = models.DateField(null=True, blank=True)
    project_end = models.DateField(null=True, blank=True)
    description = models.CharField('Descrição', max_length=150, default='')
    status = models.CharField(default="E", max_length=1, choices=STATUS_CHOICES) # Em andamento | Concluído | Em análise | Cancelado
    is_active = models.BooleanField(default=True)
    judge = models.ForeignKey(Judge, on_delete=models.PROTECT)
    layer = models.ForeignKey(Layer, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    engagement = models.ForeignKey(ProjectEngagement, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.description}"
