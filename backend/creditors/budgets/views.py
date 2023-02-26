from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from creditors.budgets.models import Budgets
from creditors.budgets.schemas import BudgetsSchema


class BudgetsApi(AbstractViewApi):
    """HTTP methods for Budgets"""
    http_method_names = ['post', 'get']
    serializer_class = BudgetsSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Budgets
    schema = AutoSchema(tags=["Creditors - Budgets"])

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
