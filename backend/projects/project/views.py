from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.project.models import Project
from projects.project.schemas import ProjectSchema
from projects.engagement.models import Engagement, ProjectEngagement


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
        numbers = engagements.pop('engagement').get('numbers', [])

        users = engagements.pop('users', [])
        project_engagement = ProjectEngagement.objects.create()  # Create ProjectEngagement
        project_engagement.users.add(*users)
        project_engagement.save()

        new_project['engagement_id'] = project_engagement.id
        project = self.model.objects.create(**new_project)  # Create Project
        project.save()

        for number in numbers:
            # Create Engagement Project number
            Engagement.objects.create(
                **{'number': number, 'project_id': project_engagement.id})

        return JsonResponse({'project': ProjectSchema(project, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Projects details"""
        projects = self.get_query()
        return JsonResponse({'projects': projects})
