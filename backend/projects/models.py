from django.db import models
from numpy import number
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
    """
    This class Project represents a grand project/engagement.
    It contains the properties project_start and project_end for specifying the start and end date of the project, 
    as well as a status field with choices specified by the constant STATUS_CHOICES. 
    Additionally it stores relations to other models such as Judge, Lawyer, and Region through foreign keys,
    as well as a one-to-one relationship to the model ProjectEngagement through the field engagement. 
    Lastly it has two fields containing relationships to the User model, namely manager and partner. 
    The property num_recovering is responsible for retrieving the number of recovering related to this project. 
    Lastly the string representation of this object is defined in the method __str__.
    """

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
    engagement = models.OneToOneField(
        ProjectEngagement, on_delete=models.PROTECT)

    @property
    def num_recovering(self) -> number:
        return self.recovering_set.all().count()

    def __str__(self):
        return f"{self.description}"
