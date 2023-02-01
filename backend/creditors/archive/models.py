from django.db import models
from core.abstract.models import AbstractModel


class Archive(models.Model):
    description = models.CharField(max_length=150)
    archive_json = models.TextField(blank=True) 

    def __str__(self):
        return f"{self.id} | {str(self.description)}"
    