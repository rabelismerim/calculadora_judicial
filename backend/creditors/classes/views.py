from core.abstract.views import AbstractViewApi

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from creditors.classes.models import Classes
from creditors.classes.schemas import ClassesSchema
from utils import _


class ClassesApi(AbstractViewApi):
    """HTTP methods for Classes"""
    http_method_names = ['post', 'get']
    serializer_class = ClassesSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Classes

    query_params = [
        {
            "name": "classe",
            "field": "classe__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Class")),
            "schema": {"type": "string"}
        }
    ]
