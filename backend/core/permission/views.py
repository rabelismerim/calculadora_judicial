from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import BasePermission
from django.apps import apps as default_apps
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.utils.translation import gettext_lazy as _

from calculation.funds.document.models import FundDocument
from calculation.funds.irrf.models import FundIRRF
from calculation.funds.models import Funds
from calculation.models import Calculation, CHOICES_STEP
from calculation.schemas import ChangeStepSerializer
from config.settings import GROUP_NAME_APPROVER, GROUP_NAME_REVIEWER, GROUP_NAME_EXECUTOR, GROUP_NAME_SPECIAL_APPROVE, \
    IS_LOCALHOST, SWAGGER_URL, BASE_URL
from projects.project_user.models import ProjectUser


class CheckHasPermission(BasePermission):
    """
    Check if the user has the correct permission to access the requested view.

    Attributes:
        None

    Methods:
        has_permission(request, view):
            Check if the user has permission to access the requested view.

            Args:
                request: the HTTP request object
                view: the view being accessed

            Returns:
                True if the user has permission, False otherwise
    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the requested view.

        Args:
            request: the HTTP request object
            view: the view being accessed

        Returns:
            True if the user has permission, False otherwise
        """
        option = {
            'GET': 'view',
            'PUT': 'change',
            'POST': 'add',
            'DELETE': 'delete',
        }

        return request.user.has_permission(f'{option.get(request.method)}_{view.model.__name__.lower()}')


class PermissionsName:
    """
    A class that provides permission codes for different user types.

    Attributes:
        _layout_perm: a string format for change permission codes
        _layout_request: a string format for request permission codes
        executor: a list of tuples containing executor permission codes
        reviewer: a list of tuples containing reviewer permission codes
        approve: a list of tuples containing approve permission codes
        special_approve: a list of tuples containing special approve permission codes

    Methods:
        check_exist_codename(text):
            Check if a given permission code exists in the list of permission codes.

            Args:
                text: the permission code to check

            Returns:
                True if the permission code exists, False otherwise
    """
    _layout_perm = 'can_change_{}_to_{}'

    executor = [
        (_layout_perm.format('r', 's'), _('Can Change failed Calculation to calculate'), 'calculation'),
        (_layout_perm.format('s', 'c'), _('Can Execute Calculation to Review'), 'calculation')
    ]

    reviewer = [
        (_layout_perm.format('c', 'e'), _('Can Reviewer Calculation to Approve'), 'calculation'),
        (_layout_perm.format('c', 'b'), _('Can Reviewer Calculation to Approve special'), 'calculation'),
        (_layout_perm.format('c', 's'), _('Can Reviewer Calculation to Calculate'), 'calculation'),
        (_layout_perm.format('c', 'r'), _('Can Reviewer Calculation to Failed'), 'calculation'),
    ]

    approve = [
        (_layout_perm.format('e', 'a'), _('Can Approve Revised Calculation'), 'calculation'),
        (_layout_perm.format('e', 'c'), _('Can Disapprove Revised Calculation to Review'), 'calculation'),
        (_layout_perm.format('e', 'r'), _('Can Disapprove Revised Calculation to Failed'), 'calculation')
    ]

    special_approve = [
        (_layout_perm.format('b', 'a'), _('Can Approve Special Calculation'), 'calculation'),
        (_layout_perm.format('b', 'c'), _('Can Disapprove Special Calculation to Review'), 'calculation'),
        (_layout_perm.format('b', 'r'), _('Can Disapprove Special Calculation to Failed'), 'calculation')
    ]

    @staticmethod
    def __get_codenames(list_codenames):
        """
        This method receives a list of codenames and returns a list containing only the first item of each nested list.
        """
        return [obj[0] for codename in list_codenames for obj in codename]

    def codenames_remove_attribute(self, attribute):
        """
        This method calls the __get_codenames method passing a list containing the "reviewer", "approve" and
        "special_approve" attributes of the object to obtain a list of codenames with the specified attribute removed.
        """
        if attribute == "executor":
            return self.__get_codenames([self.reviewer, self.approve, self.special_approve])
        elif attribute == "reviewer":
            return self.__get_codenames([self.executor, self.approve, self.special_approve])
        elif attribute == "approve":
            return self.__get_codenames([self.reviewer, self.executor, self.special_approve])
        elif attribute == "special_approve":
            return self.__get_codenames([self.reviewer, self.approve, self.executor])
        raise ValueError("Invalid attribute")

    def check_exist_codename(self, text):
        """
        Check if a given permission code exists in the list of permission codes.

        Args:
           text: the permission code to check

        Returns:
           True if the permission code exists, False otherwise
        """
        codenames = [self.executor, self.reviewer, self.approve, self.special_approve]
        for codename in codenames:
            for obj in codename:
                if text in obj[0]:
                    return True
        return False


class CreatePermissions:
    """
    A class to create Django groups with specific sets of permissions.

    Methods:
    -------
    create_group_project_manager():
        Creates a Django Group, assigns a name 'Project Manager', and adds necessary permissions.

    create_group_executor():
        Creates a Django Group, assigns a name 'Executor', and adds necessary permissions.

    create_group_reviewer():
        Creates a Django Group, assigns a name 'Reviewer', and adds necessary permissions.

    create_group_approve():
        Creates a Django Group, assigns a name 'Approver', and adds necessary permissions.

    create_group_special_approve():
        Creates a Django Group, assigns a name 'Special Approve', and adds necessary permissions.

    create_group_by_name(group_name: str):
        Creates a Django Group by the given group_name argument.

    __create_group(group_name: str, list_permissions: list):
        A private method that creates and returns a Django Group with specific permissions based on arguments.

    """

    @staticmethod
    def create_group_all_groups() -> tuple:
        """
        Returns a tuple of Project Manager group's permissions, created group instance, and a Boolean created.
        """

        project_manager_list = []
        executor_list = []
        reviewer_list = []
        approver_list = []
        special_approver_list = []
        create_group = {'name': 'Project Manager'}
        group_manager, created = Group.objects.get_or_create(defaults=create_group, **create_group)

        create_group = {'name': GROUP_NAME_EXECUTOR}
        group_executor, created = Group.objects.get_or_create(defaults=create_group, **create_group)

        create_group = {'name': GROUP_NAME_REVIEWER}
        group_reviewer, created = Group.objects.get_or_create(defaults=create_group, **create_group)

        create_group = {'name': GROUP_NAME_APPROVER}
        group_approver, created = Group.objects.get_or_create(defaults=create_group, **create_group)

        create_group = {'name': GROUP_NAME_SPECIAL_APPROVE}
        group_special_approver, created = Group.objects.get_or_create(defaults=create_group, **create_group)

        list_apps = ['creditors', 'projects', 'calculation', 'rate', 'core', 'base', 'recovering', 'rates']

        app_names = [app for app in settings.INSTALLED_APPS if '.' in app or app in list_apps]

        for app in app_names:
            app_name = app.split('.')
            app_lbl = app_name[0]
            model_name = app_name[1] if len(app_name) > 1 else app_name[0]
            app_models = default_apps.all_models[model_name]
            for model in app_models.values():
                permissions = Permission.objects.filter(content_type__app_label=model._meta.app_label,
                                                        content_type__model=model._meta.model_name
                                                        ).values_list('id', flat=True)
                if app_lbl == 'projects':
                    project_manager_list.extend(permissions)
                elif app_lbl == 'calculation':
                    perm = PermissionsName()
                    executor_list.extend(permissions.exclude(codename__in=perm.codenames_remove_attribute('executor')))
                    permissions = permissions.exclude(codename='add_calculation')

                    reviewer_list.extend(permissions.exclude(codename__in=perm.codenames_remove_attribute('reviewer')))
                    approver_list.extend(permissions.exclude(codename__in=perm.codenames_remove_attribute('approve')))
                    special_approver_list.extend(
                        permissions.exclude(codename__in=perm.codenames_remove_attribute('special_approve')))

        group_manager.permissions.add(*project_manager_list)
        group_manager.save()

        group_executor.permissions.add(*executor_list)
        group_executor.save()

        group_reviewer.permissions.add(*reviewer_list)
        group_reviewer.save()

        group_approver.permissions.add(*approver_list)
        group_approver.save()

        group_special_approver.permissions.add(*special_approver_list)
        group_special_approver.save()
        return project_manager_list, created, group_manager

    def create_group_executor(self) -> tuple:
        """
        Returns a tuple of Executor group's permissions, created group instance, and a Boolean created.
        """
        return self.__create_group(GROUP_NAME_EXECUTOR, PermissionsName.executor)

    def create_group_reviewer(self) -> tuple:
        """
        Returns a tuple of Reviewer group's permissions, created group instance, and a Boolean created.
        """
        return self.__create_group(GROUP_NAME_REVIEWER, PermissionsName.reviewer)

    def create_group_approve(self) -> tuple:
        """
        Returns a tuple of Approver group's permissions, created group instance, and a Boolean created.
        """
        return self.__create_group(GROUP_NAME_APPROVER, PermissionsName.approve)

    def create_group_special_approve(self) -> tuple:
        """
        Returns a tuple of Special Approver group's permissions, created group instance, and a Boolean created.
        """
        return self.__create_group(GROUP_NAME_SPECIAL_APPROVE, PermissionsName.special_approve)

    def create_group_by_name(self, group_name: str) -> tuple:

        return getattr(self, f'create_group_{group_name}')()

    @staticmethod
    def __create_group(group_name: str, list_permissions: list) -> tuple:
        """
        Returns a tuple of group's permissions, created group instance, and a Boolean created with
        the group_name argument.
        """
        create_group = {'name': group_name}

        # Get all existing permissions in bulk
        perms_by_codename = {
            perm.codename: perm
            for perm in Permission.objects.filter(codename__in=[p[0] for p in list_permissions])
        }

        new_perms_by_codename = {}

        # Create missing permissions in bulk
        for codename, name, app_label in list_permissions:
            if not PermissionsName().check_exist_codename(codename):
                print('Codename não existente\n')
                continue

            if codename not in perms_by_codename:
                content_type = ContentType.objects.filter(app_label=app_label).first()
                new_perms_by_codename[codename] = Permission(codename=codename, name=name, content_type=content_type)

        Permission.objects.bulk_create(new_perms_by_codename.values())
        perms_by_codename.update(new_perms_by_codename)
        # Get or create the group
        group_manager, created = Group.objects.get_or_create(**create_group)

        # Set the group's permissions
        ids = [perm.id for perm in perms_by_codename.values()]
        group_manager.permissions.add(*ids)
        group_manager.save()
        # group_manager.permissions.set(perms_by_codename.values())

        return [perm.id for perm in perms_by_codename.values()], created, group_manager


class CanChangeStep(BasePermission):
    """
    Permission check for allowing a user to change steps in a process.

    Methods:
        - has_permission(self, request, view): Checks if the requesting user has permission to change the process step.
    """
    message = 'Você não tem permissão para alterar o status nesse projeto.'

    @staticmethod
    def __get_choice_step(value: str) -> str or None:
        """
        This static method receives a string value and returns a corresponding choice from CHOICES_STEP list,
        based on the first item of each tuple. If the value is not found, it returns None.
        """
        for choice in CHOICES_STEP:
            if choice[0] == value.upper():
                return choice[1]
        return None

    def has_permission(self, request, view):
        """
        This method checks if the user has permission to change the step of a Calculation object. Receives request
        and view objects as parameters. It gets the calculation_id from the view, checks if the user has the
        necessary permission codename, and returns a boolean indicating if the user has permission or not. If the
        user doesn't have permission, it raises a ValidationError with a message indicating the current and next
        steps that cannot be changed.
        """

        user = request.user
        calculation_id = view.kwargs.get('id', None)
        if calculation_id:
            calculation = Calculation.objects.get(id=calculation_id)
            serializer = ChangeStepSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            next_step = serializer.validated_data['next_step'].lower()
            current_step = calculation.step.lower()
            codename = f'can_change_{current_step}_to_{next_step}'
            has_perm_user = ProjectUser.objects.filter(user=user, groups__permissions__codename=codename,
                                                       projectengagement__project__recovering__creditor__calculation__id=
                                                       calculation_id).exists()
            if not has_perm_user:
                return False
            has_codename = PermissionsName().check_exist_codename(codename)
            if not has_codename:
                text = _('Unable to change status from {} to {}').format(self.__get_choice_step(current_step),
                                                                         self.__get_choice_step(next_step))
                raise serializers.ValidationError([text])
            return True

        if request.path == SWAGGER_URL:
            return True
        return False


class CheckPermissions(BasePermission):
    """
    Permission check for allowing a user to change steps in a process.

    Methods:
        - has_permission(self, request, view): Checks if the requesting user has permission to change the process step.
    """
    message = _('You do not have permission. Contact admin')

    def has_permission(self, request, view):
        """
        This method checks if the user has permission to change the step of a Calculation object. Receives request
        and view objects as parameters. It gets the calculation_id from the view, checks if the user has the
        necessary permission codename, and returns a boolean indicating if the user has permission or not. If the
        user doesn't have permission, it raises a ValidationError with a message indicating the current and next
        steps that cannot be changed.
        """
        if hasattr(view, 'perms') is False:
            raise AttributeError(_('Need to add "perms: list" attribute to use CheckPermissions class'))
        perms = view.perms
        return request.user.has_permission(perms)


class CheckFundsPjPfPermissions(BasePermission):
    message = _('It is not possible to register this fund')

    def has_permission(self, request, view):
        if request.path == SWAGGER_URL:
            return True
        if hasattr(view, 'physical_person') is False:
            raise AttributeError(
                _('Need to add "physical_person: bool" attribute to use CheckFundsPjPfPermissions class'))
        calculation_id = view.request.data.get('calculation_id')
        calculation = get_object_or_404(Calculation, id=calculation_id)

        physical_person = calculation.creditor.physical_person
        if physical_person == view.physical_person:
            return True

        if physical_person:
            self.message = _('It is not possible to register a fund of the legal entity type for individuals')
        else:
            self.message = _('It is not possible to register a fund of the individuals type for legal entity')
        return False


class CheckHasFundRegisteredPermissions(BasePermission):
    message = _('it is not possible to register an agreement when there is already an fund or fund IRRF registered')

    def has_permission(self, request, view):
        if request.path == SWAGGER_URL:
            return True
        calculation_id = view.request.data.get('calculation_id')
        funds = Funds.objects.filter(calculation_id=calculation_id).exists()
        fund_irrf = FundIRRF.objects.filter(calculation_id=calculation_id).exists()
        if funds or fund_irrf:
            return False
        return True


class CheckHasAgreementRegisteredPermissions(BasePermission):
    message = _('it is not possible to register an fund when there is already an agreement registered')

    def has_permission(self, request, view):
        if request.path == SWAGGER_URL:
            return True
        calculation_id = view.request.data.get('calculation_id')
        return not FundDocument.objects.filter(calculation_id=calculation_id).exists()


class CheckAPIVersion(BasePermission):
    """
    Permission class that checks if the requested API version is supported.
    The version must be included in the URL, e.g. /api/v1/customers/.
    """

    def has_permission(self, request, view):
        """
        Check if the requested API version is supported.
        """
        # Obter a versão da API a partir da URL
        version = request.path.split('juca/api/')[1].split('/')[0]

        if request.path == SWAGGER_URL:
            return BASE_URL.split('juca/api/')[1].split('/')[0] in view.allowed_versions
        if version not in view.allowed_versions:
            # Versão API não suportada
            return False

        # A versão é suportada
        return True


def check_query_permission(perms):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            has_perm = self.request.user.has_permission(perms)
            if has_perm:
                return {}
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
