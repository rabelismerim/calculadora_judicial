from django.db import models
from core.entity.models import Entity
from recovering.models import Recovering
from base.models import AbstractDateCreditor
from utils import _


class Creditor(AbstractDateCreditor):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    recovering = models.ForeignKey(Recovering, on_delete=models.PROTECT)
    description = models.CharField(_('Description'), max_length=255, null=True)

    total = models.FloatField(_('Total sum of valid amounts'), default=0)
    total_historical = models.FloatField(_('Total historical sum of valid amounts'), default=0)

    def get_total(self) -> float:
        return self.total

    def get_total_historical(self) -> float:
        return self.total_historical

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
        return self.notice_set.all()

    def has_notice_aj(self) -> bool:
        return self.noticerecovering_set.exists()

    # def get_classes(self):
    #     return self.calculation_set.all().values_list('')
    #
    # # TODO: pegar a classe que está nos calculos, exibindo como lista

    def validate_calcs(self, calculations: list) -> tuple:
        """Receives a list of ids of calculations from the creditor and validates those ids, invalidating the
        calculations that do not have in that list"""
        # invalidates all calculations
        invalidated_calculations = self.calculation_set.filter(validated=True).exclude(id__in=calculations,
                                                                                       step='A').values_list('id',
                                                                                                             flat=True)
        invalidated = list(invalidated_calculations)
        invalidated_calculations.update(validated=False)

        # validates all calculations
        validated_calculations = self.calculation_set.filter(id__in=calculations, validated=False,
                                                             step='A').values_list('id', flat=True)
        validated = list(validated_calculations)
        validated_calculations.update(validated=True)
        self.set_total()

        return invalidated, validated

    def __str__(self):
        return f'{self.entity}'

    def save(self, *args, **kwargs):
        self.set_total(False)
        super().save(*args, **kwargs)

    def get_total_validated(self) -> tuple:
        calcs = self.calculation_set.filter(validated=True, step='A')
        total_corrected = 0
        total_historical = 0
        for calc in calcs:
            totals = calc.get_total_funds()
            total_corrected += totals['total_corrected']
            total_historical += totals['total_historical']
        return total_corrected, total_historical

    def set_total(self, commit=True):
        """Set the total value of the creditor by adding all the corrected amounts of the sums"""
        self.total, self.total_historical = self.get_total_validated()
        if commit:
            self.save()
