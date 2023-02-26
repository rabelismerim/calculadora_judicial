from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from recovering.archive.models import Archive
from recovering.archive_recovering.models import ArchiveRecovering
from recovering.archive_recovering.schemas import ArchiveRecoveringSchema


class ArchiveRecoveringApi(AbstractViewApi):
    """HTTP methods for ArchiveRecovering"""
    http_method_names = ['post', 'get']
    serializer_class = ArchiveRecoveringSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = ArchiveRecovering
    schema = AutoSchema(tags=["Recovering - Archive Recovering"])

    query_params = [
        {
            "name": "registration",
            "field": "registration__icontains",
            "in": "query",
            "required": False,
            "description": "Registro",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """
           Create ArchiveRecovering receiving a dict, return ArchiveRecovering detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_archive_recovering = serializer.validated_data
        archive = new_archive_recovering.pop('archive')
        new_archive = Archive.objects.create(**archive)
        new_archive_recovering['archive'] = new_archive
        archive_recovering = self.model.objects.create(
            **new_archive_recovering)
        return JsonResponse({'archive_recovering': self.serializer_class(archive_recovering, many=False).data}, status=status.HTTP_201_CREATED)
