from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.court.models import Court
from projects.court.schemas import CourtSchema
from utils import _


class CourtApi(AbstractViewApi):
    """HTTP methods for court"""
    http_method_names = ['post', 'get']
    serializer_class = CourtSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Court
    schema = AutoSchema(tags=[str(_("Project - Court"))])

    docs = {
        'init': _("""The `Court` represents a court (jurisdictional body) of Brazilian justice in the project. 
        It contains properties such as `description` (name of the court) It is used as a reference model to establish 
        the relationship between the `Project` class and the court that has jurisdiction over the case."""),
        'get': _("""Get the list of all courts, being able to filter by name."""),
        'post': _("""Create a new court, if it does not exist in the base, if it exists, an exception will be generated.
        Returns court details if successful.""")
    }

    query_params = [
        {
            "name": "name",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Court's name")),
            "schema": {"type": "string"}
        }
    ]
