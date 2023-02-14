from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.court.models import Court
from projects.court.schemas import CourtSchema


class CourtApi(AbstractViewApi):
    """HTTP methods for court"""
    http_method_names = ['post', 'get']
    serializer_class = CourtSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Court
    schema = AutoSchema(tags=["Project - Court"])

    query_params = [
        {
            "name": "nome",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome do Juiz",
            "schema": {"type": "string"}
        }
    ]
