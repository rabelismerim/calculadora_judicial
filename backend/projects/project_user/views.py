from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.project_user.schemas import ProjectUserSchema
from projects.project_user.models import ProjectUser
from projects.engagement.models import ProjectEngagement
from projects.models import Project
from utils import get_user_model

User = get_user_model()


class ProjectUserApi(AbstractViewApi):
    """HTTP methods for ProjectUser"""
    http_method_names = ['post', 'get']
    serializer_class = ProjectUserSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = ProjectUser
    schema = AutoSchema(tags=["Project - ProjectUser"])

    def get(self, request, *args, **kwargs):
        """
           get projects from user authenticated, return ProjectUser id
        """
        serializer = self.get_serializer_class()
        projects_user = serializer(ProjectEngagement.objects.filter(
            users__user=request.user), many=True).data
        projects_user_data = []
        for item in projects_user:
            project=Project.objects.filter(engagement=item['id'])
            if len(project)>0:
                projects_user_data.append(project[0].id)
        return JsonResponse({'project_user': projects_user_data}, status=status.HTTP_200_OK)



    def post(self, request, *args, **kwargs):
        """
           Create ProjectUser receiving a dict, return ProjectUser detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_project_user = serializer.validated_data.pop('user')
        project_user = self.model.objects.create(
            user=User.objects.filter(id=new_project_user).first())
        project_user.save()
        project_user_data = self.serializer_class(
            project_user, many=False).data
        project_user_data['id'] = project_user.id
        return JsonResponse({'project_user': project_user_data}, status=status.HTTP_201_CREATED)
