from django.db import models
from core.abstract.models import AbstractModel
from projects.project_user.models import ProjectUser


class ProjectEngagement(AbstractModel):
    users = models.ManyToManyField(ProjectUser, blank=True)

    @property
    def list_engagements(self):
        return list(self.engagement_set.all().values_list('number', flat=True))

    @property
    def project_id(self):
        return self.project.id

    @property
    def user_names(self):
        return list(self.users.all().values(username=models.F('user__username')))


class Engagement(AbstractModel):
    number = models.CharField('Numero do engagement',
                              max_length=10, unique=True)
    project = models.ForeignKey(ProjectEngagement, on_delete=models.PROTECT)

    def __str__(self):
        return self.number
