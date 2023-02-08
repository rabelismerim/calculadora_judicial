from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.lawyer.models import Lawyer
from projects.lawyer.schemas import LawyerSchema


class LawyerApi(AbstractViewApi):
    """HTTP methods for Lawyer"""
    http_method_names = ['post', 'get']
    serializer_class = LawyerSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Lawyer
    schema = AutoSchema(tags=["Lawyer"])

    query_params = [
        {
            "name": "nome",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome do advogado",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """
           Create Lawyer receiving a dict, return Lawyer detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_lawyer = serializer.validated_data
        lawyer = self.model.objects.create(**new_lawyer)
        lawyer.save()
        return JsonResponse({'lawyer': self.serializer_class(lawyer, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get lawyers details"""
        lawyers = self.get_query()
        return JsonResponse({'lawyers': lawyers})
