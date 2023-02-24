from calculation.criterion.models import Criterion
from calculation.criterion.schemas import CriterionSchema
from core.abstract.views import AbstractViewApi
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission


class CriterionApi(AbstractViewApi):
    """Define the CriterionApi view class for handling HTTP methods related to criterion.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CriterionApi supports HTTP POST and GET methods, and uses the CriterionSchema
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
        To retrieve criterion with a matching description:
        ```
        GET /api/v1/criterion/?sentenca=sentenca_name
        ```
    """
    http_method_names = ['get']
    serializer_class = CriterionSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Criterion
    schema = AutoSchema(tags=["Calculation - Criterion"])

    query_params = [
        {
            "name": "sentenca",
            "field": "calculation__description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome da Sentença",
            "schema": {"type": "string"}
        }
    ]
