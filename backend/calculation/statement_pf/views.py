"""
This module defines a StatementPFApi class that provides HTTP methods for managing Statement_Pf objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The StatementPFApi class uses the Statement_Pf model and Statement_PfSchema for working with data.
"""


from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from calculation.statement_pf.models import StatementPF
from calculation.statement_pf.schemas import StatementPFSchema


class StatementPFApi(AbstractViewApi):
    """Define the StatementPFApi view class for handling HTTP methods related to StatementPF.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementPFApi supports HTTP POST and GET methods, and uses the StatementPFSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.
        schema (AutoSchema): An OpenAPI schema object for generating API documentation.
        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve statement_pf with a matching description:
        ```
        GET /api/v1/statement_pf/?statement_pf=statement_pf_name
        ```
    """
    http_method_names = ['get']
    serializer_class = StatementPFSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = StatementPF
    schema = AutoSchema(tags=["Calculation - StatementPF"])

    query_params = [
        {
            "name": "statement_pf",
            "field": "statement_pf__icontains",
            "in": "query",
            "required": False,
            "description": "statement_pf",
            "schema": {"type": "string"}
        }
    ]
