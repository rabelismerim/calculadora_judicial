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

    project_start = models.DateField(null=True, blank=True)
    project_end = models.DateField(null=True, blank=True)
    description = models.CharField('Descrição', max_length=150, default='')
    status = models.CharField(default="E", max_length=1) # Em andamento | Concluído | Em análise | Cancelado
    is_active = models.BooleanField(default=True)
    judge = models.ForeignKey(Judge, on_delete=models.PROTECT, null=True)
    layer = models.ForeignKey(Layer, on_delete=models.PROTECT, null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    engagement = models.ForeignKey(ProjectEngagement, on_delete=models.PROTECT, null=True)
    # users = models.ManyToManyField(ProjectUser, blank=True)

    # @property
    # def engagements(self):
    #     return list(self.projectengagement_set.all().values('id', 'create_user', 'update_user',
    #      'created_at', 'updated_at', number=F('engagement__number')))


    def __str__(self):
        return f"{self.description}"
