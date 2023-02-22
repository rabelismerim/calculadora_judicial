from django.db import models
from core.abstract.models import AbstractModel
from recovering.models import Recovering
from recovering.archive.models import Archive


class ArchiveRecovering(AbstractModel):
    recovering = models.ForeignKey(Recovering, on_delete=models.PROTECT)
    archive = models.ForeignKey(Archive, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.id} | {str(self.recovering)}"
