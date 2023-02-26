from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.region.models import Region
from projects.region.schemas import RegionSchema


class RegionApi(AbstractViewApi):
    """HTTP methods for Region"""
    http_method_names = ['post', 'get']
    serializer_class = RegionSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Region
    schema = AutoSchema(tags=["Project - Region - Comarca"])

    query_params = [
        {
            "name": "nome",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome da Comarca",
            "schema": {"type": "string"}
        }
    ]
