from django.db import models
from projects.abstract_project.models import AbstractDescription


class Archive(AbstractDescription):
    archive_json = models.TextField(blank=True) 

    def __str__(self):
        return f"{self.id} | {str(self.description)}"
