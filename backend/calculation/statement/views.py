"""
This module defines a StatementApi class that provides HTTP methods for managing Statement objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The StatementApi class uses the Statement model and StatementSchema for working with data.
"""

from calculation.statement.schemas import StatementSchema
from calculation.statement.models import Statement
from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission


class StatementApi(AbstractViewApi):
    """Define the StatementApi view class for handling HTTP methods related to Statement.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementApi supports HTTP POST and GET methods, and uses the StatementSchema
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
        To retrieve statement with a matching description:
        ```
        GET /api/v1/statement/?statement=statement_name
        ```
    """
    http_method_names = ['get']
    serializer_class = StatementSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Statement
    schema = AutoSchema(tags=["Calculation - Statement - Extrato contábil"])

    query_params = [
        {
            "name": "statement",
            "field": "statement__icontains",
            "in": "query",
            "required": False,
            "description": "statement",
            "schema": {"type": "string"}
        }
    ]
