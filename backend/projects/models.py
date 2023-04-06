from django.db import models
from numpy import number
from base.models import AbstractDateRecovering, AbstractDescription
from projects.court.models import Court
from projects.judge.models import Judge
from projects.lawyer.models import Lawyer
from projects.region.models import Region
from projects.engagement.models import ProjectEngagement
from utils import get_user_model

User = get_user_model()
STATUS_CHOICES = (
    ('E', 'Em Preparação'),
    ('C', 'Concluído'),
    ('A', 'Em Andamento'),
    ('F', 'Cancelado'),
)


class Project(AbstractDescription, AbstractDateRecovering):
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
    process_number = models.CharField("Número do processo", max_length=25)

    status = models.CharField(default="E", max_length=1, choices=STATUS_CHOICES)
    is_adm = models.BooleanField(default=True)  # É administrativa ou judicial
    judge = models.ForeignKey(Judge, on_delete=models.PROTECT)
    lawyer = models.ForeignKey(Lawyer, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    court = models.ForeignKey(Court, on_delete=models.PROTECT)
    competence = models.CharField(
        "Competência", max_length=150, null=True)
    legal_manager = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='legal_manager', null=True)  # Gerente jurídico
    calculation_manager = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='calculation_manager', null=True)  # Gerente de calculos
    financial_manager = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='financial_manager', null=True)  # Gerente Financeiro
    legal_partner = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='legal_partner', null=True)  # Socio jurídico
    financial_partner = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='financial_partner', null=True)  # Socio Financeiro
    engagement = models.OneToOneField(ProjectEngagement, on_delete=models.PROTECT)

    @property
    def num_recovering(self) -> number:
        return self.recovering_set.all().count()

    def __str__(self):
        return f"{self.description}"
