from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import ProtectedError

from config.settings import GROUP_NAME_APPROVER, GROUP_NAME_EXECUTOR, GROUP_NAME_REVIEWER, GROUP_NAME_SPECIAL_APPROVE
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status

from rest_framework import permissions
from core.entity.models import Entity
from core.permission.views import CheckHasPermission, check_query_permission
from projects.models import Project
from projects.project_user.models import ProjectUser
from projects.schemas import ProjectSchema, ProjectListSchema, ProjectV2Schema, ProjectEditSchema
from projects.engagement.models import Engagement, ProjectEngagement
from recovering.models import Recovering
from utils import get_user_model, _, doc

User = get_user_model()


class AbstractProjectApi(AbstractViewApi):
    """HTTP methods for Project"""
    serializer_class = ProjectSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Project
    http_method_names = ['get']

    docs = {
        'init': _("""The `Project` class represents a large project/engagement in a legal or administrative process. It 
        contains properties like `project_start` and `project_end` to specify the start and end date of the project, 
        as well as a `status` field with choices specified by the `STATUS_CHOICES`
        """),

        'get': _("""Get the list of projects, with some information about it, 
        being able to filter by process_number, status, description and engagement number"""),

    }
    query_params = [
        {
            "name": "description",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Description")),
            "schema": {"type": "string"}
        },
        {
            "name": "process_number",
            "field": "process_number__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Process number")),
            "schema": {"type": "string"}
        },
        {
            "name": "status",
            "field": "status__icontains",
            "in": "query",
            "required": False,
            "description": "Status",
            "schema": {"type": "string"}
        },
        {
            "name": "engagement",
            "field": "engagement__engagement__number__icontains",
            "in": "query",
            "required": False,
            "description": "Engagement",
            "schema": {"type": "string"}
        },
    ]
    perms = ['can_view_all_projects']

    @check_query_permission(perms)
    def get_queryset(self):
        return {'engagement__users__user': self.request.user}


class ProjectDetailApi(AbstractProjectApi):  # V1
    """HTTP methods for Project Detail"""
    serializer_class = ProjectSchema
    http_method_names = ['get', 'put']
    layout_serializers = {
        'default': ProjectSchema,
        'get': ProjectSchema,
        'put': ProjectEditSchema,
    }

    @doc(_("""Update the project and roles.

        :return:
            - JsonResponse: An HTTP response containing with Project detail.
        """))
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data_obj = serializer.validated_data
        executors = data_obj.pop('executors', [])
        approver = data_obj.pop('approvers', [])
        special_approvers = data_obj.pop('special_approvers', [])
        reviewers = data_obj.pop('reviewers', [])
        request.data.pop('executors', [])
        request.data.pop('approvers', [])
        request.data.pop('special_approvers', [])
        request.data.pop('reviewers', [])

        users = []
        project = self.model.objects.filter(id=kwargs.get('id')).first()

        project_engagement = project.engagement
        project_users = project.get_project_users()

        group_executor, created = Group.objects.get_or_create(
            name=GROUP_NAME_EXECUTOR)
        group_approver, created = Group.objects.get_or_create(
            name=GROUP_NAME_APPROVER)
        group_special, created = Group.objects.get_or_create(
            name=GROUP_NAME_SPECIAL_APPROVE)
        group_reviewer, created = Group.objects.get_or_create(
            name=GROUP_NAME_REVIEWER)

        old_executors_ids = list(project_users.filter(
            groups=group_executor).values_list('user_id', flat=True))
        old_approver_ids = list(project_users.filter(
            groups=group_approver).values_list('user_id', flat=True))
        old_special_ids = list(project_users.filter(
            groups=group_special).values_list('user_id', flat=True))
        old_reviewer_ids = list(project_users.filter(
            groups=group_reviewer).values_list('user_id', flat=True))

        executors_include = [
            val for val in executors if val not in old_executors_ids]
        approver_include = [
            val for val in approver if val not in old_approver_ids]
        special_include = [
            val for val in special_approvers if val not in old_special_ids]
        reviewer_include = [
            val for val in reviewers if val not in old_reviewer_ids]

        for user_django_id in executors_include:
            project_user = ProjectUser.objects.create(user_id=user_django_id)
            project_user.groups.add(group_executor.id)
            project_user.save()
            users.append(project_user.id)

        for user_django_id in approver_include:
            project_user = ProjectUser.objects.create(user_id=user_django_id)
            project_user.groups.add(group_approver.id)
            project_user.save()
            users.append(project_user.id)

        for user_django_id in special_include:
            project_user = ProjectUser.objects.create(user_id=user_django_id)
            project_user.groups.add(group_special.id)
            project_user.save()
            users.append(project_user.id)

        for user_django_id in reviewer_include:
            project_user = ProjectUser.objects.create(user_id=user_django_id)
            project_user.groups.add(group_reviewer.id)
            project_user.save()
            users.append(project_user.id)

        executors_remove = [
            val for val in old_executors_ids if val not in executors]
        approver_remove = [
            val for val in old_approver_ids if val not in approver]
        special_remove = [
            val for val in old_special_ids if val not in special_approvers]
        reviewers_remove = [
            val for val in old_reviewer_ids if val not in reviewers]

        filters = {'projectengagement__project': project}

        users_delete = ProjectUser.objects.filter(
            user_id__in=executors_remove, groups=group_executor, **filters)
        for user_delete in users_delete:
            try:
                user_delete.delete()
            except ProtectedError:
                project_engagement.users.remove(user_delete.id)
        users_delete = ProjectUser.objects.filter(
            user_id__in=approver_remove, groups=group_approver, **filters)
        for user_delete in users_delete:
            try:
                user_delete.delete()
            except ProtectedError:
                project_engagement.users.remove(user_delete.id)
        users_delete = ProjectUser.objects.filter(
            user_id__in=special_remove, groups=group_special, **filters)
        for user_delete in users_delete:
            try:
                user_delete.delete()
            except ProtectedError:
                project_engagement.users.remove(user_delete.id)
        users_delete = ProjectUser.objects.filter(
            user_id__in=reviewers_remove, groups=group_reviewer, **filters)
        for user_delete in users_delete:
            try:
                user_delete.delete()
            except ProtectedError:
                project_engagement.users.remove(user_delete.id)
        project_engagement.users.add(*users)
        project_engagement.save()
        return super().put(request, *args, **kwargs)


class ProjectDetailV2Api(AbstractProjectApi):  # V2
    """HTTP methods for Project Detail"""
    serializer_class = ProjectV2Schema
    http_method_names = ['get', 'put']
    allowed_versions = ['v1', 'v2']
    layout_serializers = {
        'default': ProjectV2Schema,
        'get': ProjectV2Schema,
        'put': ProjectEditSchema,
    }


class ProjectApi(AbstractProjectApi):
    """HTTP methods for Project"""
    http_method_names = ['post', 'get']

    layout_serializers = {
        'default': ProjectListSchema,
        'get': ProjectListSchema,
        'post': ProjectSchema,
    }
    pagination = True

    @doc(_("""Create Project receiving a dict, return project detail"""))
    def post(self, request, *args, **kwargs):

        with transaction.atomic():
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_project = dict(serializer.validated_data)

            recoverings = new_project.pop('recovering_set')
            engagements = new_project.pop('engagement')
            executors = new_project.pop('executors', [])
            approvers = new_project.pop('approvers', [])
            special_approvers = new_project.pop('special_approvers', [])
            reviewers = new_project.pop('reviewers', [])

            users = []

            group_executor, created = Group.objects.get_or_create(
                name=GROUP_NAME_EXECUTOR)
            group_approver, created = Group.objects.get_or_create(
                name=GROUP_NAME_APPROVER)
            group_special, created = Group.objects.get_or_create(
                name=GROUP_NAME_SPECIAL_APPROVE)
            group_reviewer, created = Group.objects.get_or_create(
                name=GROUP_NAME_REVIEWER)

            for user_django_id in executors:
                project_user = ProjectUser.objects.create(
                    user_id=user_django_id)
                project_user.groups.add(group_executor.id)
                project_user.save()
                users.append(project_user.id)
            for user_django_id in approvers:
                project_user = ProjectUser.objects.create(
                    user_id=user_django_id)
                project_user.groups.add(group_approver.id)
                project_user.save()
                users.append(project_user.id)
            for user_django_id in reviewers:
                project_user = ProjectUser.objects.create(
                    user_id=user_django_id)
                project_user.groups.add(group_reviewer.id)
                project_user.save()
                users.append(project_user.id)
            for user_django_id in special_approvers:
                project_user = ProjectUser.objects.create(
                    user_id=user_django_id)
                project_user.groups.add(group_special.id)
                project_user.save()
                users.append(project_user.id)

            project_engagement = ProjectEngagement.objects.create()  # Create ProjectEngagement
            project_engagement.users.add(*users)
            project_engagement.save()

            new_project['engagement_id'] = project_engagement.id
            project = self.model.objects.create(
                **new_project)  # Create Project

            for number in engagements:  # Create Engagement Project number
                Engagement.objects.create(
                    **{'number': number, 'project_id': project_engagement.id})

            for recovering in recoverings:
                entity = recovering.pop('entity')
                new_archive_recovering = recovering.pop('archives', None)
                recovering['project'] = project

                recovering['entity'], created = Entity.objects.get_or_create(defaults=entity,
                                                                             **{'legal_number': entity.get(
                                                                                 'legal_number')})
                new_recovering = Recovering.objects.get_or_create(**recovering)
                # if new_archive_recovering: # TODO: fase 2. Desativado na fase 1
                #     for new_ in new_archive_recovering:
                #         archive = new_.pop('archive')
                #         new_archive = Archive.objects.create(**archive)
                #         ArchiveRecovering.objects.create(
                #             recovering=new_recovering, archive=new_archive)

        return JsonResponse({'project': self.serializer_class(project, many=False).data},
                            status=status.HTTP_201_CREATED)
