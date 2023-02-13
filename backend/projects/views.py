from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.entity.models import Entity
from core.permission.views import CheckHasPermission
from projects.models import Project
from projects.schemas import ProjectCreateSchema, ProjectSchema, ProjectListSchema
from projects.engagement.models import Engagement, ProjectEngagement
from recovering.archive.models import Archive
from recovering.archive_recovering.models import ArchiveRecovering
from recovering.models import Recovering
from utils import get_user_model
User = get_user_model()


class AbstractProjectApi(AbstractViewApi):
    """HTTP methods for Project"""
    serializer_class = ProjectSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Project
    http_method_names = ['get']
    # exclude = ('recoverings', 'status_display')
    schema = AutoSchema(tags=["Project"])

    query_params = [
        {
            "name": "descrição",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Descrição do projeto",
            "schema": {"type": "string"}
        }
    ]

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

    def get_serializer_class(self):
        print(self, 'self\n')
        return self.layout_serializers.get(self.request.method.lower(),
                                           self.layout_serializers['default'])

    def post(self, request, *args, **kwargs):
        """
           Create Project receiving a dict, return project detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_project = dict(serializer.validated_data)

        recoverings = new_project.pop('recovering_set')
        engagements = new_project.pop('engagements')

        users = new_project.pop('users', [])
        users = [x['id'] for x in users]

        project_engagement = ProjectEngagement.objects.create()  # Create ProjectEngagement
        project_engagement.users.add(*users)
        project_engagement.save()

        new_project['engagement_id'] = project_engagement.id
        project = self.model.objects.create(**new_project)  # Create Project

        for number in engagements:  # Create Engagement Project number
            Engagement.objects.create(
                **{'number': number, 'project_id': project_engagement.id})

        for recovering in recoverings:
            entity = recovering.pop('entity')
            new_archive_recovering = recovering.pop('archives', None)
            recovering['project'] = project
            recovering['entity'] = Entity.objects.create(**entity)
            new_recovering = Recovering.objects.create(**recovering)
            if new_archive_recovering:
                for new_ in new_archive_recovering:
                    archive = new_.pop('archive')
                    new_archive = Archive.objects.create(**archive)
                    ArchiveRecovering.objects.create(
                        recovering=new_recovering, archive=new_archive)

        return JsonResponse({'project': self.serializer_class(project, many=False).data}, status=status.HTTP_201_CREATED)
