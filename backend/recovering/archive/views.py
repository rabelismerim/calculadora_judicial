from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from recovering.archive.models import Archive
from recovering.archive.schemas import ArchiveSchema


class ArchiveApi(AbstractViewApi):
    """HTTP methods for Archive"""
    http_method_names = ['post', 'get']
    serializer_class = ArchiveSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
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
