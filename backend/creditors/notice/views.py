from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from creditors.notice.models import Notice
from creditors.notice.schemas import NoticeSchema


class NoticeApi(AbstractViewApi):
    """HTTP methods for Notice"""
    http_method_names = ['post', 'get']
    serializer_class = NoticeSchema
    permission_classes = [permissions.IsAdminUser]
    model = Notice
    schema = AutoSchema(tags=["Creditors - Notice - Edital"])

    query_params = [
        {
            "name": "valor",
            "field": "value__icontains",
            "in": "query",
            "required": False,
            "description": "Valor",
            "schema": {"type": "string"}
        }
    ]
