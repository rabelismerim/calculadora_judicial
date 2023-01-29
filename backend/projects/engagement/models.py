from django.db import models
from core.abstract.models import AbstractModel
from projects.project.models import Project
from projects.project_user.models import ProjectUser


class Engagement(AbstractModel):
    number = models.CharField('Numero do engagement', max_length=10)

    def __str__(self):
        return self.number


class ProjectEngagement(AbstractModel):
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    engagement = models.ForeignKey(Engagement, on_delete=models.PROTECT)
    users = models.ManyToManyField(ProjectUser, blank=True)

    def __str__(self):
        return f'{self.project} - {self.engagement}'