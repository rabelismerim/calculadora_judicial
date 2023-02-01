from django.db import models
from core.abstract.models import AbstractModel


class ArchiveRecovering(models.Model):
    id_recovering = models.ForeignKey("creditors.recovering", on_delete=models.CASCADE, related_name="Recuperanda")
    id_archive = models.ForeignKey("creditors.archive", on_delete=models.CASCADE, related_name="Arquivo")
    
    def __str__(self):
        return f"{self.id} | {str(self.id_recovering)}"
    