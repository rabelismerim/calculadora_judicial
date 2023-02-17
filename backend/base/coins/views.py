from core.abstract.views import AbstractViewApi
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from base.coins.models import Coins
from base.coins.schemas import CoinsSchema


class CoinsApi(AbstractViewApi):
    """Define the CoinsApi view class for handling HTTP methods related to coins.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CoinsApi supports HTTP POST and GET methods, and uses the CoinsSchema
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
        To create a new coin:
        ```
        POST /api/v1/coins/
        {
            "coin": "B",
            "value": 0
        }
        ```
        To retrieve coins with a matching description:
        ```
        GET /api/v1/coins/?description=B
        ```
    """

    http_method_names = ['post', 'get']
    serializer_class = CoinsSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Coins
    schema = AutoSchema(tags=["Base - Coins"])

    query_params = [
        {
            "name": "description",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Descrição",
            "schema": {"type": "string"}
        }
    ]
