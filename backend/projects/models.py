from django.db import models
from base.models import AbstractDescription
from projects.court.models import Court
from projects.judge.models import Judge
from projects.lawyer.models import Lawyer
from projects.region.models import Region
from projects.engagement.models import ProjectEngagement
from utils import get_user_model

User = get_user_model()
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
    court = models.ForeignKey(Court, on_delete=models.PROTECT)
    manager = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='manager')
    partner = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='partner')
    engagement = models.ForeignKey(ProjectEngagement, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.description}"
