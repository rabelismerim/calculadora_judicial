from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from projects.judge.models import Judge
from projects.judge.schemas import JudgeSchema
from utils import _


class JudgeApi(AbstractViewApi):
    """HTTP methods for judge"""
    http_method_names = ['post', 'get']
    serializer_class = JudgeSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Judge
    schema = AutoSchema(tags=[str(_("Project - Judge"))])

    docs = {
        'init': _("""The `Judge` represents a judge (jurisdictional body) of Brazilian justice in the project. 
            It contains properties such as `description` (name of the judge) It is used as a reference model to 
            establish the relationship between the `Project` class and the judge that has jurisdiction over the case.
            """),

        'get': _("""Get the list of all judges, being able to filter by name."""),
        'post': _("""Create a new judge, if it does not exist in the base, if it exists, an exception will be generated.
            Returns judge details if successful.""")
    }

    query_params = [
        {
            "name": "name",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Judge's name")),
            "schema": {"type": "string"}
        }
    ]
