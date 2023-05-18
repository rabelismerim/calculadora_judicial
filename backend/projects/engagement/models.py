from django.db import models
from core.abstract.models import AbstractModel
from projects.project_user.models import ProjectUser
from utils import _


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

    def __str__(self):
        return str(self.project) if hasattr(self, 'project') else f'{self.user_names}'


class Engagement(AbstractModel):
    number = models.CharField(_('Engagement number'), max_length=100, unique=True)
    project = models.ForeignKey(ProjectEngagement, on_delete=models.PROTECT)

    def __str__(self):
        return self.number
