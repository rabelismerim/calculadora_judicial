from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects import engagement
from projects.project.models import Project
from projects.project.schemas import ProjectSchema
from projects.engagement.models import Engagement, ProjectEngagement
from projects.project_user.models import ProjectUser


class ProjectApi(AbstractViewApi):
    """HTTP methods for Project"""
    http_method_names = ['post', 'get']
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

    def post(self, request, *args, **kwargs):
        """
           Create Project receiving a dict, return project detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_project = serializer.validated_data

        engagements = new_project.pop('engagement')
        numbers = [x['number'] for x in engagements]

        users = new_project.pop('users', [])
        list_users = []
        users = [x['id'] for x in users]

        project_engagement = ProjectEngagement.objects.create()  # Create ProjectEngagement
        project_engagement.users.add(*list_users)
        project_engagement.save()

        new_project['engagement_id'] = project_engagement.id
        project = self.model.objects.create(
            **new_project)  # Create Project
        project.save()

        for number in numbers:
            # Create Engagement Project number
            Engagement.objects.create(
                **{'number': number, 'project_id': project_engagement.id})

        return JsonResponse({'project': ProjectSchema(project, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Projects details"""
        filters = {'engagement__users__user': request.user}
        projects = self.get_query(**filters)
        return JsonResponse({'projects': projects})
