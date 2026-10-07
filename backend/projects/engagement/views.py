from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.engagement.models import ProjectEngagement, Engagement
from projects.engagement.schemas import ProjectEngagementSchema
from utils import _, doc


class EngagementApi(AbstractViewApi):
    """HTTP methods for Engagement"""
    http_method_names = ['post', 'get']
    serializer_class = ProjectEngagementSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = ProjectEngagement

    query_params = [
        {
            "name": "number",
            "field": "engagement__number",
            "in": "query",
            "required": False,
            "description": str(_("Engagement number")),
            "schema": {"type": "string"}
        }
    ]

    docs = {
        'init': _("""The engagement is the unique control number, which references the client/project in the Sistema.
        """),
        'get': _("""Get the list of all engagements, being able to filter by number."""),
    }

    @doc(_("""Create Engagement receiving a dict, return Engagement detail"""))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_engagement = serializer.validated_data

        users = new_engagement.pop('users')

        numbers = new_engagement.pop('engagement')
        project_engagement, created = self.model.objects.get_or_create(
            project__id=new_engagement['project_id'])  # Get or Create ProjectEngagement
        project_engagement.users.add(*users)
        project_engagement.save()
        for number in numbers:
            Engagement.objects.create(
                **{'number': number, 'project_id': project_engagement.id})  # Create Engagement Project number
        return JsonResponse({'engagement': self.serializer_class(project_engagement, many=False).data},
                            status=status.HTTP_201_CREATED)
