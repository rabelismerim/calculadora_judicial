from django.db import models
from projects.abstract_project.models import AbstractDescription
from projects.judge.models import Judge
from projects.lawyer.models import Lawyer
from projects.region.models import Region
from projects.engagement.models import ProjectEngagement


STATUS_CHOICES = (
    ('P', 'Em Preparação'),
    ('C', 'Concluido'),
    ('A', 'Em Andamento'),
    ('F', 'Cancelado'),
)


class Project(AbstractDescription):
    '''Class responsible for the grand project/engagement'''

    project_start = models.DateField(null=True, blank=True)
    project_end = models.DateField(null=True, blank=True)

    status = models.CharField(
        default="E", max_length=1, choices=STATUS_CHOICES)
    is_adm = models.BooleanField(default=True)  # É adminstrativa ou judicial
    judge = models.ForeignKey(Judge, on_delete=models.PROTECT)
    lawyer = models.ForeignKey(Lawyer, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    engagement = models.ForeignKey(ProjectEngagement, on_delete=models.PROTECT)

    @property
    def status_display(self):
        return self.get_status_display

    def __str__(self):
        return f"{self.description}"
