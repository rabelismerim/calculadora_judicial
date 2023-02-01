from django.db import models
from core.abstract.models import AbstractModel


class Budgets(models.Model):
    
    description = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.id}"
    