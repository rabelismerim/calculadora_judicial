"""
Defines an model for objects.
Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Does not add any additional fields, so should be subclassed
to add specific fields as needed.
"""
import datetime
import logging

from base.claim.models import ClaimCreditor
from base.coins.models import Coins
from base.models import CHOICES_OCCURRENCE
from calculation.comparative.signals import new_calc
from calculation.premise.models import Premise
from config.settings import (GROUP_NAME_APPROVER, GROUP_NAME_EXECUTOR,
                             GROUP_NAME_REVIEWER, GROUP_NAME_SPECIAL_APPROVE)
from core.abstract.models import AbstractModel
from creditors.classes.models import CLASSE_CHOICES
from creditors.models import Creditor
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from projects.project_user.models import ProjectUser
from rates.models import Rate
from rest_framework import serializers
from utils import check_choice

CHOICES_STEP = (
    ('S', _('To Calculate')),
    ('C', _('To Review')),
    ('E', _('To Approve')),
    ('B', _('To Approve Special')),
    ('A', _('Finalized')),
    # ('R', _('Failed'))
)


class Incident(AbstractModel):
    """
    # Statement A5

    The Incident class is a subclass of the AbstractModel, representing an incident that can occur during the execution
    of a process. It has one attribute:

    Attributes:
        - number (models.CharField): The number of the incident represented as a character field with a maximum length
            of 100.
    """
    # Statement A5
    number = models.CharField(_('Incident number'), max_length=100)


class SpecialApprover(AbstractModel):
    """
    # Statement A5

    The Incident class is a subclass of the AbstractModel, representing an incident that can occur during the execution
    of a process. It has one attribute:

    Attributes:
        - number (models.CharField): The number of the incident represented as a character field with a maximum length
            of 100.
    """
    project_user = models.ForeignKey(ProjectUser, on_delete=models.PROTECT)
    approved = models.BooleanField(_('Approved'), default=False)


class Calculation(AbstractModel):
    """
    Attributes:
        creditor (models.ForeignKey): The creditor associated with the calculation.
        incident (models.ForeignKey): The incident associated with the calculation.
        step (models.CharField): The step of the calculation (S for survivor or D for deceased).
        appeal_credit (models.BooleanField): Is the credit entirely concursal?
        validated (models.BooleanField): Validated?
        appeal_deposit (models.BooleanField): Has an appeal deposit been made?
        has_advocative_hours (models.BooleanField): Are there any advocative fees in the homologous calculation?
        date_credit_auth (models.DateField): The date of the credit authorization certificate.
        has_edital (models.BooleanField): Is there an Article 7 Section 2 - 11.101/2005 Edital?
    """
    creditor = models.ForeignKey(Creditor, on_delete=models.CASCADE)
    step = models.CharField(_('Calculation step'),
                            max_length=1, choices=CHOICES_STEP, default='S')
    number = models.CharField(_('Calculation number'),
                              max_length=10, null=True, blank=True)
    recurral_deposit = models.FloatField(
        _('Recurral deposit released'), default=0)
    validated = models.BooleanField(_('Validated?'), default=False)

    # Statement A5
    coins = models.ForeignKey(Coins, on_delete=models.CASCADE, null=True)
    claims = models.ManyToManyField(ClaimCreditor, blank=True)

    appeal_credit = models.BooleanField(
        _('Fully competitive credit?'), default=False)
    # Statement Q5 - Data do calculo homologado
    date_approved_calculation = models.DateField(
        _('Approved calculation date'), null=True)

    # Statement N7 - Levantamento de depósito recursal?
    appeal_deposit = models.BooleanField(
        _('Recursal deposit withdrawal?'), default=False)
    # Statement Q7 - Página que mostra o levantamento de depósito recursal
    num_pag_fls_appeal_deposit = models.CharField(_('Page number of the appeal deposit withdrawal'), max_length=10,
                                                  null=True, blank=True)

    # Statement N9 - Data da certidão de habilitação de crédito
    date_credit_auth = models.DateField(
        _('Date of credit qualification certificate'), null=True)
    # Statement Q9 - Página da certidão de habilitação de crédito
    num_pag_fls_credit_auth_date = models.CharField(_('Credit qualification certificate page'), max_length=10,
                                                    null=True, blank=True)
    # Statement N10 - Há honorários advocatícios?
    has_advocative_hours = models.BooleanField(
        _('Are there fees in the approved calculation?'), default=False)

    rate = models.ForeignKey(
        Rate, on_delete=models.PROTECT, null=True, blank=True)
    date_rj_filing = models.DateField(
        _("RJ filing date"), blank=True, null=True)
    date_citation = models.DateField(_("Citation Date"), blank=True, null=True)
    occurrence = models.CharField(
        _('Occurrence'), max_length=1, choices=CHOICES_OCCURRENCE, default='O')

    @property
    def incident_number(self):
        claim = self.claims.first()
        if claim:
            return claim.incident.number
        return ''

    @property
    def has_edital(self):
        return self.creditor.has_notice_aj()

    premises = models.ManyToManyField(Premise, blank=True)
    is_adm = models.BooleanField(default=True)  # É administrativa ou judicial

    approver = models.ForeignKey(
        ProjectUser, on_delete=models.PROTECT, null=True, related_name='approver', blank=True)
    # special_approver = models.ForeignKey(ProjectUser, on_delete=models.PROTECT, null=True,
    #                                      # TODO: transformar em listas, ter um campo de controle para aprovado
    #                                      related_name='special_approver', blank=True)
    special_approvers = models.ManyToManyField(SpecialApprover, blank=True)
    executor = models.ForeignKey(
        ProjectUser, on_delete=models.PROTECT, null=True, related_name='executor', blank=True)
    reviewer = models.ForeignKey(
        ProjectUser, on_delete=models.PROTECT, null=True, related_name='reviewer', blank=True)

    def get_premises(self):
        return self.premises.all()

    @property
    def executor_name(self):
        if self.executor:
            return self.executor.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.codenames_to_special_approve = [
            f'can_change_{self.get_step_to_approve_special()}_to_{self.get_step_to_approve_special()}',
            f'can_change_{self.get_step_to_approve()}_to_{self.get_step_to_approve_special()}']
        self.special_approve_to_approved = f'can_change_{self.get_step_to_approve_special()}_to_{self.get_step_approved()}'
        self.user_groups = {
            GROUP_NAME_EXECUTOR: 'executor_id',
            GROUP_NAME_APPROVER: 'approver_id',
            GROUP_NAME_REVIEWER: 'reviewer_id'
        }

    class Meta:
        ordering = ('-created_at', '-updated_at')

    def __str__(self):
        return f'{self.creditor.entity.name} || {self.number} || {self.get_step_display()}'

    def _get_number(self) -> str:
        """:return: the number of calculations for the creditor."""
        return f'{self._get_count_process_calculation() + 1} - {self.creditor.get_count_calculations() + 1}'

    def _get_count_process_calculation(self) -> int:
        """:return: the count of Calculation objects for the creditor's project"""
        return Calculation.objects.filter(creditor__recovering__project=self.creditor.recovering.project).exclude(
            number__isnull=True).count()

    def save(self, *args, **kwargs):
        get_statement = self.get_statement()
        super(Calculation, self).save(*args, **kwargs)

        if not self.rate:
            raise serializers.ValidationError([_('Need a rate')])

        if not self.id or not self.number:
            self.number = self._get_number()
        if not get_statement:
            self.create_statement()

    def create_statement(self):
        try:
            new_calc.send(sender=self.__class__, instance=self)
        except Exception as e:
            logging.error(e, exc_info=True)

    def get_rate(self) -> Rate:
        """
        Excel Analysis sheet B20

        Get rate
        """
        return self.rate

    def get_date_rj(self) -> datetime.date or None:
        """
        Excel Analysis sheet D66, Statement B18

        Get date RJ request
        """
        return self.criterion.date_rj_request

    def get_default_interest(self) -> float:
        """
        Excel Analysis sheet D66, Statement B21

        Get value of default interest
        """
        return self.criterion.default_interest

    def get_legend_default_interest(self):
        """
        Extrato contábil A21
        =SE(OU($B$19>=$B$18;'Ficha de Análise'!D65="IPCA-E/SELIC");"EXCLUIR LINHA";'Ficha de Análise'!C66)
        """
        # TODO: ver erro no extrato contábil ao nao usar date rj filling or date_rj
        if (self.get_date_rj_filing() >= self.get_date_rj()) or self.rate.is_ipca_e_selic():
            return
        return 'Juros moratórios (a.m.)'

    def get_dismissal(self) -> datetime.date or None:
        """
        Excel Analysis sheet D62

        Get dismissal date
        """
        return self.criterion.dismissal

    def get_has_advocative_hours(self) -> bool:
        """
        Excel Statement N10

        Get has advocative hours
        """
        return self.has_advocative_hours

    def get_advocative_hours(self) -> float:
        """
        Excel Analysis sheet D68, Statement B23

        Get value in % of attorney fees
        """
        return self.criterion.advocative_hours

    def get_legend_advocative_hours(self):
        """
        Extrato contábil A22
        =SE(OU('Ficha de Análise'!D67="";'Ficha de Análise'!D67=0);"EXCLUIR LINHA";"Multa moratória")
        """
        if self.get_advocative_hours() > 0:
            return 'Honorários advocatícios'

    def get_date_approved_calculation(self) -> datetime.date or None:
        """Get the approved calculation date"""
        # TODO verificar com stakeholders o momento que essa data é recebida, se há alterações ao longo do processo.
        #  Com isso criar o field em calculo, recuperanda ou credor
        return self.date_approved_calculation

    def get_fine(self) -> float:
        """
        Excel Analysis sheet D67, Statement B22

        Get value of fine
        """
        return self.criterion.fine

    def get_legend_fine(self):
        """
        Extrato contábil A22
        =SE(OU('Ficha de Análise'!D67="";'Ficha de Análise'!D67=0);"EXCLUIR LINHA";"Multa moratória")
        """
        if self.get_fine() > 0:
            return 'Multa moratória'

    def get_appeal_credit(self) -> bool:
        """
        Excel Statement N5

        Get if the credit is entirely bankrupt
        """
        return self.appeal_credit

    def get_appeal_deposit(self) -> bool:
        """
        Excel Statement N7

        Get if it is Recursal deposit withdrawal
        """
        return self.appeal_deposit

    def get_date_credit_auth(self) -> datetime.date or None:
        """
        Excel Statement N9

        Get the date of the credit qualification certificate
        """
        return self.date_credit_auth

    def get_num_pag_fls_appeal_deposit(self) -> str or None:
        """
        Excel Statement Q7

        Get the number of the page that was quoted the withdrawal of the appeal deposit
        """
        return self.num_pag_fls_appeal_deposit

    def get_lawyer(self) -> str:
        """
        Excel Analysis sheet A50

        Get lawyer name
        """
        return self.creditor.recovering.project.lawyer.description

    def get_project_user(self, user, codename):
        """
        :return: a ProjectUser object that represents the given user assigned to a group with a specific permission codename.

        :param user: User instance for which a ProjectUser object will be retrieved.
        :param codename: The codename of the permission that the group must have.
        :return: A ProjectUser object representing the user if it exists, None otherwise.
        """
        return ProjectUser.objects.filter(user=user, groups__permissions__codename=codename,
                                          projectengagement__project__recovering__creditor__calculation__id=self.id).values(
            'id', group_name=F('groups__name')).first()

    def get_complete_project_user(self, user, codename):
        """
        :return: a ProjectUser object that represents the given user assigned to a group with a specific permission codename.

        :param user: User instance for which a ProjectUser object will be retrieved.
        :param codename: The codename of the permission that the group must have.
        :return: A ProjectUser object representing the user if it exists, None otherwise.
        """
        return ProjectUser.objects.filter(user=user, groups__permissions__codename=codename,
                                          projectengagement__project__recovering__creditor__calculation__id=self.id).annotate(
            group_name=F('groups__name')).first()

    def get_step_to_approve(self):
        return 'e'

    def get_step_to_approve_special(self):
        return 'b'

    def get_step_approved(self):
        return 'a'

    def set_step_by_char(self, next_step: str, user=None, special_approvers=None):
        """
        Sets the current step of the project engagement to a new value represented by a character.

        :param next_step: The character representing the new step of the project engagement. Must be one of CHOICES_STEP.
        :param user: User instance of the user executing the change. If given, the function checks if this user has the
        appropriate permission to execute the step change.
        :param special_approvers: List of Special Approvers when alter step to Approve for to Approve Especial or
        to Approve Especial for to Approve Especial
        :raises: ValidationError if the user doesn't have the appropriate permission or is already assigned to another
        role in the project.
        """
        if not special_approvers:
            special_approvers = []
        check_choice(next_step, CHOICES_STEP)
        if user:
            codename = f'can_change_{self.step.lower()}_to_{next_step.lower()}'
            user_executed = self.get_complete_project_user(user, codename)
            if user_executed:

                if codename in self.special_approve_to_approved:
                    self._approve_special_calculation(user)
                else:
                    self._set_step_user(user, next_step, special_approvers)

    def _approve_special_calculation(self, user):
        """
        Sets the given user's special approval flag for this calculation to True.

        If the given user does not have permission to approve the calculation, or if they have already approved it, raises
        a validation error.

        Args:
            user (django.contrib.auth.models.User): The Django User object representing the user.

        Raises:
            serializers.ValidationError: If the user does not have permission to specially approve the calculation,
            or if the user has already specially approved the calculation.
        """
        user_special = self.special_approvers.filter(
            project_user__user=user).first()
        if not user_special:
            raise serializers.ValidationError(
                [_('You do not have permission to specially approve this calculation')])
        if user_special.approved:
            raise serializers.ValidationError(
                [_('You have already specially approved this calculation, wait for the other approvers')])
        user_special.approved = True
        user_special.save()
        self._check_approve_special_calculation()

    def _check_approve_special_calculation(self):
        """
        Checks whether all special approvers have approved this calculation.

        If the step is the one where special approvers need to approve the calculation and all special approvers have
        approved, sets the step to the next step and saves the object.
        """
        if self.step == self.get_step_to_approve_special().upper():
            has_pending_approval = self.special_approvers.filter(
                approved=False).exists()
            if has_pending_approval is False:
                self.step = self.get_step_approved().upper()
                self.save()

    def _set_step_user(self, user, next_step, special_approvers=None):
        """
        Sets the current step to the given next step, and sets the user for the group that is allowed to change to the next step.

        If the user can change the step to the next step according to their group permissions, sets the user
        for the corresponding step group. Raises a validation error if the user is already allocated to another role in
        the same project. If the next step requires special approvers, sets them using the provided list.

        Args:
            user (django.contrib.auth.models.User): The Django User object representing the user.
            next_step (str): A string representing the next step in the process.
            special_approvers (list, optional): A list of Django User IDs representing the special approvers.
                Defaults to None.

        Raises:
            serializers.ValidationError: If the user cannot change the step to the next step according to their group
            permissions, or if the user is already allocated to another role in the same project.
        """
        codename = f'can_change_{self.step.lower()}_to_{next_step.lower()}'
        user_executed = self.get_complete_project_user(user, codename)
        approve_calculation = codename in self.codenames_to_special_approve
        if user_executed:
            group_name = user_executed.group_name
            user_groups = self.user_groups.copy()
            if group_name in user_groups:
                selected_group = user_groups.pop(group_name)

                if approve_calculation:
                    self._set_special_approvers(special_approvers)

                self.__check_user_already_allocated(
                    [user_executed.user.id], selected_group=group_name)
                setattr(self, selected_group, user_executed.id)

        self.step = next_step
        self.validated = False
        self.save()
        if approve_calculation:
            self._check_approve_special_calculation()

    def __check_user_is_special_approver(self, special_approvers: list):
        """
        Checks that each user in the given list is a special approver in the project.

        Args:
            special_approvers (list): A list of Django User IDs representing the users to check.

        :return:
            QuerySet: A QuerySet of ProjectUser objects representing the special approvers in the project.

        Raises:
            serializers.ValidationError: If any user in the list is not a special approver in the project.
        """

        # Get list of project users with permission special approve to approved
        project_users = self.creditor.recovering.project.get_project_users().filter(
            groups__permissions__codename=self.special_approve_to_approved)
        # groups__permissions__codename=self.special_approve_to_approved)

        users_not_in_project = [
            spe for spe in special_approvers if not project_users.filter(id=spe).exists()]
        if users_not_in_project:
            users = ProjectUser.objects.filter(
                id__in=users_not_in_project).values_list('user__username', flat=True)
            raise serializers.ValidationError(
                [_('The users: {} are not allocated in the project as a special approver'.format(', '.join(users)))])
        project_users_filtered = project_users.filter(id__in=special_approvers)
        return project_users_filtered

    def __check_user_already_allocated(self, django_user_ids: list, selected_group=None):
        """
        Raises a validation error if any user is already allocated to another role in the same project.

        Args:
            django_user_ids (list): A list of Django User IDs representing the users to check.
            selected_group (str, optional): The name of a group to exclude from the check. Defaults to None.

        Raises:
            serializers.ValidationError: If any user is already allocated to another role in the same project.
        """
        user_groups = self.user_groups.copy()
        if selected_group:
            user_groups.pop(selected_group)
        for group in user_groups.values():
            group_attribute = getattr(self, group.replace('_id', ''))
            if group_attribute and group_attribute.user.id in django_user_ids:
                raise serializers.ValidationError(
                    _('The user {} is already in the role of {}, not being able to have two or more roles in '
                      'the same project').format(group_attribute.user.get_full_name,
                                                 group.replace('_id', '').replace('_', ' ').title()))

    def _set_special_approvers(self, special_approvers: list):
        """
        Sets the list of special approvers for this object. If the list is empty, raises a validation error.
        Checks that each user in the list is a special approver in the project.
        Checks that a user is not already allocated to another role in the same project.
        Creates new SpecialApprover objects as necessary, and adds them to this object's special approvers.
        Deletes any existing special approvers that are not in the new list of special approvers and have not been approved.
        Raises a validation error if any user in the new list of special approvers has already been approved.

        Args:
            special_approvers (list): A list of Django User IDs representing the new special approvers.

        Raises:
            serializers.ValidationError: If the list of special approvers is empty, or if any user in the new list of
            special approvers is not a special approver in the project, or if a user is already allocated to another role
            in the same project, or if any user in the new list of special approvers has already been approved.
        """
        # Check empty list
        if not special_approvers:
            raise serializers.ValidationError(
                [_('The list of special approvers is empty')])
        project_users = self.__check_user_is_special_approver(
            special_approvers)

        users_django_ids = list(
            project_users.values_list('user__id', flat=True))
        self.__check_user_already_allocated(users_django_ids)

        specials = SpecialApprover.objects.filter(
            project_user__id__in=special_approvers, approved=False)
        special_approvers_list = self.special_approvers.all()
        special_approvers_approved = self.special_approvers.filter(project_user__id__in=special_approvers,
                                                                   approved=True)

        specials_ids = []
        specials_bulk = []
        for approver_id in special_approvers:
            user_special = special_approvers_approved.filter(
                project_user__id=approver_id).first()
            if user_special:  # User already registered
                specials_ids.append(user_special.id)
                continue
            special = specials.filter(project_user_id=approver_id).first()
            if not special:
                special = SpecialApprover(
                    project_user_id=approver_id, approved=False)
                specials_bulk.append(special)
            specials_ids.append(special.id)

        SpecialApprover.objects.bulk_create(specials_bulk)
        special_approvers_list.exclude(
            id__in=specials_ids).exclude(approved=True).delete()
        self.special_approvers.add(*specials_ids)
        # self._check_approve_special_calculation()

    def get_total_summed(self):
        return 0

    def get_classes(self) -> list:
        """
        Groups the Funds, Fund Documents, and FundIRRF by class and calculates the total value and total calculated
        amount for each class.

        :return: a list of dictionaries containing the class name, total value, total calculated amount, percentage of
        total value, and percentage of total calculated amount for each class. Only classes where at least one fund,
        fund document, or fund IRRF exists are included in the results.

        :return: List of dictionaries containing the class totals.
        :rtype: list
        """
        classes = [{'classe': fund.classes.classe,
                    'total_value': fund.coins.value,
                    'coin': fund.coins.get_coin_display(),
                    'total_calculated': fund.get_total_summed()} for fund in
                   self.funds_set.filter(classes__classe__isnull=False)]
        classes += [{'classe': fund.classes.classe,
                     'total_value': fund.coins.value,
                     'coin': fund.coins.get_coin_display(),
                     'total_calculated': fund.get_total_summed()} for fund in
                    self.funddocument_set.filter(classes__classe__isnull=False)]
        classes += [{'classe': fund.classes.classe,
                     'total_value': fund.coins.value,
                     'coin': fund.coins.get_coin_display(),
                     'total_calculated': fund.get_total_summed()} for fund in
                    self.fundirrf_set.filter(classes__classe__isnull=False)]

        classes += [{'classe': fund.classes.classe,
                     'total_value': fund.coins.value,
                     'coin': fund.coins.get_coin_display(),
                     'total_calculated': fund.get_total_summed()} for fund in
                    self.funddanos_set.filter(classes__classe__isnull=False)]

        classes += [{'classe': fund.classes.classe,
                     'total_value': fund.coins.value,
                     'coin': fund.coins.get_coin_display(),
                     'total_calculated': fund.get_total_summed()} for fund in
                    self.funddeduction_set.filter(classes__classe__isnull=False)]

        class_totals = {}
        total_value_sum = 0
        total_calculated_sum = 0
        quantity_by_classes = []
        for class_dict in classes:
            class_name = class_dict['classe']
            quantity_by_classes.append(class_name)
            class_total_value = class_dict['total_value']
            class_total_calculated = class_dict['total_calculated']
            total_value_sum += class_total_value
            total_calculated_sum += class_total_calculated
            if class_name not in class_totals:
                class_totals[class_name] = {
                    'coin': class_dict['coin'],
                    'total_value': class_total_value,
                    'total_calculated': class_total_calculated}
            else:
                class_totals[class_name]['total_value'] += class_total_value
                class_totals[class_name]['total_calculated'] += class_total_calculated
                class_totals[class_name]['coin'] = class_dict['coin']
        for class_dict in class_totals.values():
            total_calculated = class_dict['total_calculated']
            total_value = class_dict['total_value']
            class_dict['percentage_calculated'] = (
                                                          total_calculated / total_calculated_sum) * 100 if total_calculated_sum > 0 else 0
            class_dict['percentage_value'] = (
                                                     total_value / total_value_sum) * 100 if total_value_sum > 0 else 0

        classes_list = []
        classes_list_included = []
        classes_choices = dict(CLASSE_CHOICES)

        for class_name, total in class_totals.items():
            obj = {'classe': class_name, 'classes_display': classes_choices.get(class_name),
                   'total_value': total['total_value'], 'total_calculated': total['total_calculated'],
                   'percentage_value': total.get('percentage_value', 0),
                   'coin': total.get('coin'),
                   'quantity': quantity_by_classes.count(class_name),
                   'percentage_calculated': total.get('percentage_calculated', 0)}
            classes_list.append(obj)
            classes_list_included.append(class_name)
        for key, value in CLASSE_CHOICES:
            if key not in classes_list_included:
                obj = {'classe': key, 'classes_display': value,
                       'total_value': 0, 'total_calculated': 0,
                       'percentage_value': 0,
                       'quantity': 0,
                       'coin': '',
                       'percentage_calculated': 0}
                classes_list.append(obj)
        return classes_list

    def get_total_funds(self) -> dict:
        """Add up the corrected amounts of the sums"""
        total_corrected = 0
        total_historical = 0

        for fund in self.funds_set.all():
            total_corrected += fund.get_total_summed()
            total_historical += fund.get_total_historical_summed()

        for fund in self.funddocument_set.all():
            total_corrected += fund.get_total_summed()
            total_historical += fund.get_total_historical_summed()

        for fund in self.fundirrf_set.all():
            total_corrected += fund.get_total_summed()
            total_historical += fund.get_total_historical_summed()

        return {'total_corrected': total_corrected, 'total_historical': total_historical}

    def get_big_number_calc(self) -> dict:
        """Count of all registered funds"""
        total = self.funds_set.all().count()
        total += self.funddocument_set.all().count()
        total += self.fundirrf_set.all().count()

        classes = [{'classe': fund.classes.classe, 'total_value': fund.coins.value,
                    'total_calculated': fund.get_total_summed(),
                    'total_historical': fund.get_total_historical_summed(),
                    } for fund in
                   self.funds_set.filter(classes__classe__isnull=False)]
        classes += [{'classe': fund.classes.classe, 'total_value': fund.coins.value,
                     'total_calculated': fund.get_total_summed(),
                     'total_historical': fund.get_total_historical_summed(), } for fund in
                    self.funddocument_set.filter(classes__classe__isnull=False)]
        classes += [{'classe': fund.classes.classe, 'total_value': fund.coins.value,
                     'total_calculated': fund.get_total_summed(),
                     'total_historical': 0} for fund in
                    self.fundirrf_set.filter(classes__classe__isnull=False)]

        classes += [{'classe': fund.classes.classe, 'total_value': fund.coins.value,
                     'total_calculated': fund.get_total_summed(),
                     'total_historical': fund.get_total_historical_summed(), } for fund in
                    self.funddanos_set.filter(classes__classe__isnull=False)]

        classes += [{'classe': fund.classes.classe, 'total_value': fund.coins.value,
                     'total_calculated': fund.get_total_summed(),
                     'total_historical': fund.get_total_historical_summed(), } for fund in
                    self.funddeduction_set.filter(classes__classe__isnull=False)]

        total = 0
        total_historical = 0
        count = len(classes)
        for class_dict in classes:
            total += class_dict['total_calculated']
            total_historical += class_dict['total_historical']
        return {'count_funds': count, 'count_classes': count, "total": total, "total_historical": total_historical}

    def get_date_rj_filing(self) -> datetime.date or None:  # B19
        """
        Excel Analysis sheet B19

        =IF('Ficha de Análise'!$F$66='citação';'Ficha de Análise'!D64;'Ficha de Análise'!D63)
        :return: the 'date_rj_filing' value from criteria if occurrence is 'C',
        otherwise returns the 'date_citation' value from criteria

        If either date_rj_filing or date_citation does not exist, sets an error value and returns None
        """
        if self.is_citation():
            date_citation = self.get_date_citation()
        else:
            date_citation = self.get_rj_filling()
        return date_citation

    def get_rj_filling(self):
        """:return: 'date_rj_filing' from calculation"""
        return self.date_rj_filing

    def get_date_citation(self) -> datetime.date or None:
        """:return: 'date_citation' from calculation"""
        return self.date_citation

    def get_date_rj_request(self) -> datetime.date or None:
        """
        Excel Analysis sheet B18

        :return: 'date_rj_request' from statement criteria If date_rj_request does not exist, sets an error value and
        returns None
        """
        return self.criterion.date_rj_request

    def is_citation(self) -> bool:
        """
        Excel analysis sheet C64

        Get if the occurrence in criterion is of type citation
        """
        return self.occurrence == 'C'

    def is_filing(self) -> bool:
        """
        Excel analysis sheet C64

        Get if the occurrence in criterion is of type filing"""
        return self.occurrence == 'A'

    def get_statement(self):
        """
        Gets the statement attribute of the object if it exists.

        :return:
            - The statement attribute of the object, if it exists.
            - None, otherwise.
        """
        return getattr(self, 'statement', None)

    def is_agreement(self) -> bool:
        """
        Excel Statement A78

        See if the calculations are for agreements
        """

        # TODO ver se o credor do tipo PF tem acordos feitos
        statement = self.get_statement()
        if statement:
            return True if statement.get_statement_pj() else False
        return False

    def invalidate_calculation(self):
        if self.validated:
            self.validated = False
            self.save()
            self.creditor.set_total()

    def get_total_funds_danos(self) -> float:
        """Add up the corrected amounts of the sums"""
        total_corrected = 0

        for fund in self.funddanos_set.all():
            total_corrected += fund.get_total_due_summed()

        return total_corrected


class StepAction:
    class Option:
        def __init__(self, name, lst):
            self.name = name
            self.lst = lst

    def __init__(self, current_step, next_step):
        self.current_step = current_step
        self.next_step = next_step
        options = [
            self.Option(GROUP_NAME_EXECUTOR, [('r', 's'), ('s', 'c')]),
            self.Option(GROUP_NAME_REVIEWER, [
                ('c', 'e'), ('c', 'b'), ('c', 's'), ('c', 'r')]),
            self.Option(GROUP_NAME_APPROVER, [
                ('e', 'a'), ('e', 'c'), ('e', 'r')]),
            self.Option(GROUP_NAME_SPECIAL_APPROVE, [
                ('b', 'a'), ('b', 'c'), ('b', 'r')])
        ]

        self.options = {o.name: o.lst for o in options}

    def compare_options(self):
        for name, lst in self.options.items():
            if (self.current_step.lower(), self.next_step.lower()) in lst:
                return name
        return None
