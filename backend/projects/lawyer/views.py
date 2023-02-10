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
    schema = AutoSchema(tags=["Project - Lawyer"])

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
