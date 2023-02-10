from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from base.coins.models import Coins
from base.coins.schemas import CoinsSchema


class CoinsApi(AbstractViewApi):
    """HTTP methods for Coins"""
    http_method_names = ['post', 'get']
    serializer_class = CoinsSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Coins
    schema = AutoSchema(tags=["Base - Coins"])

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
