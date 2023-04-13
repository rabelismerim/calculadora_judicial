from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
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
    schema = AutoSchema(tags=[str(_("Creditors - Classes"))])

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
