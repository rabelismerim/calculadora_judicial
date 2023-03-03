"""
This module defines a Api's classes that provides HTTP methods for managing Comparative objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the Comparative model and schema Comparative to work with data.
"""


from calculation.comparative.schemas import ComparativeSchema
from calculation.comparative.models import Comparative
from core.abstract.views import AbstractViewApi
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission


class ComparativeApi(AbstractViewApi):
    """Define the ComparativeApi view class for handling HTTP methods related to Comparative.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The ComparativeApi supports HTTP POST and GET methods, and uses the ComparativeSchema
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
        To retrieve comparative with a matching description:
        ```
        GET /api/v1/comparative/?comparative=comparative_name
        ```
    """
    http_method_names = ['get']
    serializer_class = ComparativeSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Comparative
    schema = AutoSchema(tags=["Comparative"])

    query_params = [
        {
            "name": "comparative",
            "field": "comparative__icontains",
            "in": "query",
            "required": False,
            "description": "comparative",
            "schema": {"type": "string"}
        }
    ]
