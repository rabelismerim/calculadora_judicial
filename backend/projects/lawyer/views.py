from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.lawyer.models import Lawyer
from projects.lawyer.schemas import LawyerSchema
from utils import _


class LawyerApi(AbstractViewApi):
    """HTTP methods for Lawyer"""
    http_method_names = ['post', 'get']
    serializer_class = LawyerSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Lawyer
    schema = AutoSchema(tags=[str(_("Project - Lawyer"))])

    docs = {
        'init': _("""The `Lawyer` represents a lawyer (jurisdictional body) of Brazilian justice in the project. 
                It contains properties such as `description` (name of the lawyer) It is used as a reference model to 
                establish the relationship between the `Project` class and the lawyer that has jurisdiction over the 
                case.
                """),
        'get': _("""Get the list of all lawyers, being able to filter by name.
        """),
        'post': _("""Create a new lawyer, if it does not exist in the base, if it exists, an exception will be generated.
                Returns lawyer details if successful.
                """)
    }

    query_params = [
        {
            "name": "name",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Lawyer's name")),
            "schema": {"type": "string"}
        }
    ]
