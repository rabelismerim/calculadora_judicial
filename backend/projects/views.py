from django.contrib.auth.models import Group
from django.db import transaction

from config.settings import GROUP_NAME_APPROVER, GROUP_NAME_EXECUTOR, GROUP_NAME_REVIEWER
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status

from rest_framework import permissions
from core.entity.models import Entity
from core.permission.views import CheckHasPermission, check_query_permission
from projects.models import Project
from projects.project_user.models import ProjectUser
from projects.schemas import ProjectSchema, ProjectListSchema
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


class ProjectDetailApi(AbstractProjectApi):
    """HTTP methods for Project Detail"""
    serializer_class = ProjectSchema
    http_method_names = ['get']


class ProjectApi(AbstractProjectApi):
    """HTTP methods for Project"""
    http_method_names = ['post', 'get']

    layout_serializers = {
        'default': ProjectListSchema,
        'get': ProjectListSchema,
        'post': ProjectSchema,
    }

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
            reviewers = new_project.pop('reviewers', [])

            users = []

            group_executor, created = Group.objects.get_or_create(
                name=GROUP_NAME_EXECUTOR)
            group_approver, created = Group.objects.get_or_create(
                name=GROUP_NAME_APPROVER)
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
