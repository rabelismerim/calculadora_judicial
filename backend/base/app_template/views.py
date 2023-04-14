"""
This module defines a Api's classes that provides HTTP methods for managing {{app_name | title}} objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the {{app_name | title}} model and schema {{app_name | title}} to work with data.
"""


from {{app_name}}.schemas import {{app_name | title}}Schema
from {{app_name}}.models import {{app_name | title}}
from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission


class {{app_name | title}}Api(AbstractViewApi):
    """Define the {{app_name | title}}Api view class for handling HTTP methods related to {{app_name | title}}.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The {{app_name | title}}Api supports HTTP POST and GET methods, and uses the {{app_name | title}}Schema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve {{app_name}} with a matching description:
        ```
        GET /api/v1/{{app_name}}/?{{app_name}}={{app_name}}_name
        ```
    """
    http_method_names = ['get']
    serializer_class = {{app_name | title}}Schema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = {{app_name | title}}
    schema = AutoSchema(tags=["{{app_name | title}}"])

    query_params = [
        {
            "name": "{{app_name}}",
            "field": "{{app_name}}__icontains",
            "in": "query",
            "required": False,
            "description": "{{app_name}}",
            "schema": {"type": "string"}
        }
    ]
