from django.db import models
from core.entity.models import Entity
from recovering.models import Recovering
from base.models import AbstractDateCreditor
from utils import _


class Creditor(AbstractDateCreditor):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    recovering = models.ForeignKey(Recovering, on_delete=models.PROTECT)
    description = models.CharField(_('Description'), max_length=255, null=True)

    def get_count_calculations(self) -> int:
        """Get number of calculations"""
        return self.calculation_set.exclude(number__isnull=True).count()

    def get_claims_creditor(self):
        return self.claimcreditor_set.all()

    def get_claim_lawyer(self):
        if hasattr(self, 'claimlawyer'):
            return self.claimlawyer
        return None

    def get_notice(self):
        if hasattr(self, 'notice'):
            return self.notice
        return None

    # def get_classes(self):
    #     return self.calculation_set.all().values_list('')
    #
    # # TODO: pegar a classe que está nos calculos, exibindo como lista

    def validate_calcs(self, calculations: list):
        """Receives a list of ids of calculations from the creditor and validates those ids, invalidating the
        calculations that do not have in that list"""
        self.calculation_set.filter(creditor=self, validated=True).exclude(id__in=calculations, step='A').update(
            validated=False)  # invalidates all calculations
        self.calculation_set.filter(creditor=self, id__in=calculations, validated=False, step='A').update(
            validated=True)  # validates all calculations

    def __str__(self):
        return f'{self.entity}'
