from django.db import models
from core.entity.models import Entity
from recovering.models import Recovering
from base.models import AbstractDateCreditor


class Creditor(AbstractDateCreditor):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    recovering = models.ForeignKey(
        Recovering, on_delete=models.PROTECT)
    description = models.CharField('Descrição', max_length=255, null=True)

    def get_count_calculations(self) -> int:
        """Get number of calculations"""
        return self.calculation_set.exclude(number__isnull=True).count()

    def get_clain_creditor(self):
        if hasattr(self, 'claimcreditor'):
            return self.claimcreditor
        return None

    def get_clain_lawyer(self):
        if hasattr(self, 'claimlawyer'):
            return self.claimlawyer
        return None

    def get_notice(self):
        if hasattr(self, 'notice'):
            return self.notice
        return None

    def __str__(self):
        return f'{self.entity}'
