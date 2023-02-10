from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from recovering.models import Recovering
from recovering.schemas import RecoveringSchema


class RecoveringApi(AbstractViewApi):
    """HTTP methods for Recovering"""
    http_method_names = ['post', 'get']
    serializer_class = RecoveringSchema
    permission_classes = [permissions.IsAdminUser]
    model = Recovering
    schema = AutoSchema(tags=["Recovering"])

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
