from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.judge.models import Judge
from projects.judge.schemas import JudgeSchema


class JudgeApi(AbstractViewApi):
    """HTTP methods for judge"""
    http_method_names = ['post', 'get']
    serializer_class = JudgeSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Judge
    schema = AutoSchema(tags=["Project - Judge"])

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
