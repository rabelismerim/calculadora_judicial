from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.region.models import Region
from projects.region.schemas import RegionSchema
from utils import _


class RegionApi(AbstractViewApi):
    """HTTP methods for Region"""
    http_method_names = ['post', 'get']
    serializer_class = RegionSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Region
    schema = AutoSchema(tags=[str(_("Project - Region"))])

    docs = {
        'init': _("""The `Region` represents a region (jurisdictional body) of Brazilian justice in the project. 
                    It contains properties such as `description` (name of the region) It is used as a reference model to 
                    establish the relationship between the `Project` class and the region that has jurisdiction over the 
                    case.
                    """),
        'get': _("""Get the list of all regions, being able to filter by name.
        """),
        'post': _("""Create a new region, if it does not exist in the base, if it exists, an exception will be 
        generated.
            Returns region details if successful.
            """)
    }

    query_params = [
        {
            "name": "name",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Region's name")),
            "schema": {"type": "string"}
        }
    ]
