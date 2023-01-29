from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from projects.project.models import Project
from projects.project.schemas import ProjectSchema 


class ProjectApi(AbstractViewApi):
    """HTTP methods for Project"""
    http_method_names = ['post', 'get']
    serializer_class = ProjectSchema
    permission_classes = [permissions.IsAdminUser]
    model = Project
    schema = AutoSchema(tags=["Project"])

    query_params = [
        {
            "name": "client",
            "field": "client__icontains",
            "in": "query",
            "required": False,
            "description": "Nome do cliente",
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
        print(new_project, 'project')
        project = self.model.objects.create(**new_project)
        project.save()
        return JsonResponse({'project': ProjectSchema(project, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Projects details"""
        projects = self.get_query()
        return JsonResponse({'projects': projects})