from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from creditors.archive.models import Archive
from creditors.archive.schemas import ArchiveSchema


class ArchiveApi(AbstractViewApi):
    """HTTP methods for Archive"""
    http_method_names = ['post', 'get']
    serializer_class = ArchiveSchema
    permission_classes = [permissions.IsAdminUser]
    model = Archive
    schema = AutoSchema(tags=["Creditors - Archive"])

    query_params = [
        {
            "name": "description",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Descrição",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """
           Create Archive receiving a dict, return Archive detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_archive = serializer.validated_data
        archive = self.model.objects.create(**new_archive)
        archive.save()
        return JsonResponse({'archive': self.serializer_class(archive, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Archive details"""
        archives = self.get_query()
        return JsonResponse({'archives': archives})
