from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.models import Project
from projects.schemas import ProjectCreateSchema, ProjectSchema
from projects.engagement.models import Engagement, ProjectEngagement
from utils import get_user_model
User = get_user_model()


class AbstractProjectApi(AbstractViewApi):
    """HTTP methods for Project"""
    serializer_class = ProjectSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Project
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
    http_method_names = ['get']


class ProjectCreateApi(AbstractProjectApi):
    """HTTP methods for Project Create"""
    http_method_names = ['get']
    serializer_class = ProjectCreateSchema

    query_params = []

    def get(self, request, *args, **kwargs):
        """Abstract method for default get model. Overide method in class for custom operation"""
        data = {}
        for key, field in self.serializer_class(many=False).fields.items():
            data[key] = list(field.data)
        return JsonResponse({'options': data}, status=status.HTTP_200_OK)


class ProjectApi(AbstractProjectApi):
    """HTTP methods for Project"""
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        """
           Create Project receiving a dict, return project detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_project = serializer.validated_data

        engagements = new_project.pop('engagements')

        users = new_project.pop('users', [])
        list_users = []
        users = [x['id'] for x in users]

        project_engagement = ProjectEngagement.objects.create()  # Create ProjectEngagement
        project_engagement.users.add(*list_users)
        project_engagement.save()

        new_project['engagement_id'] = project_engagement.id
        project = self.model.objects.create(**new_project)  # Create Project

        for number in engagements:  # Create Engagement Project number
            Engagement.objects.create(
                **{'number': number, 'project_id': project_engagement.id})

        return JsonResponse({'project': self.serializer_class(project, many=False).data}, status=status.HTTP_201_CREATED)
