from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from creditors.classes.models import Classes
from creditors.classes.schemas import ClassesSchema


class ClassesApi(AbstractViewApi):
    """HTTP methods for Classes"""
    http_method_names = ['post', 'get']
    serializer_class = ClassesSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Classes
    schema = AutoSchema(tags=["Creditors - Classes"])

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
