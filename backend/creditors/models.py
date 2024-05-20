import datetime

from base.models import AbstractDateCreditor, AbstractDescription
from core.entity.models import Entity
from django.db import models
from rates.models import Rate
from recovering.models import Recovering
from utils import _, is_valid_cpf, is_valid_cnpj

CHOICES_STATUS_LEGAL = (('U', _('Under review')),
                        ('P', _('Pending')), ('C', _('Concluded')))


class Creditor(AbstractDateCreditor):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    recovering = models.ForeignKey(Recovering, on_delete=models.CASCADE)
    description = models.CharField(_('Description'), max_length=255, null=True, blank=True)

    total = models.FloatField(_('Total sum of valid amounts'), default=0)
    total_historical = models.FloatField(_('Total historical sum of valid amounts'), default=0)
    is_active = models.BooleanField(_('Is active'), default=True)
    rate = models.ForeignKey(Rate, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def physical_person(self):
        return is_valid_cpf(self.entity.legal_number)

    @property
    def legal_number(self):
        return self.entity.legal_number

    @property
    def person_type(self):
        if is_valid_cpf(self.entity.legal_number):
            return _('Pessoa Física')

        if is_valid_cnpj(self.entity.legal_number):
            return _('Pessoa Jurídica')

        return _('Pessoa Estrangeira')

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
        return getattr(self, 'claimlawyer', None)

    def get_notice(self):
        return self.notice_set.all()

    def has_notice_aj(self) -> bool:
        return self.noticerecovering_set.exists()

    def get_entity_name(self):
        return self.entity.name

    def get_entity_legal_number(self):
        return self.entity.legal_number

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
        validated_calculations.update(
            validated=True, date_approved_calculation=datetime.datetime.now())
        self.set_total()

        return invalidated, validated

    def __str__(self):
        return f'{self.entity}'

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

    def _get_project(self):
        return self.recovering.project

    def get_calculation_impediment_list(self):
        impediment_list = self.legalpendencies_set.exclude(status='C')
        impediment_list = [
            _('Legal Pending: {}, has the status {}').format(
                impediment.description, impediment.get_status_display())
            for impediment in impediment_list]

        if self.representation_documentation != 'R':
            impediment_list.append(_('The representation documents have the status {}').format(
                self.get_representation_documentation_display()))
        project = self._get_project()

        date_rj_request = project.date_rj_request
        if not date_rj_request:
            impediment_list.append(_('Not found recovery request date'))

        return impediment_list

    def get_nature_description(self):
        return self.nature.all().values_list('description', flat=True)


class LegalPendencies(AbstractDescription):
    creditor = models.ForeignKey(Creditor, on_delete=models.CASCADE)
    status = models.CharField(
        _('Status'), max_length=1, choices=CHOICES_STATUS_LEGAL)
    deadline = models.DateField(_('Response deadline'), null=True, blank=True)
