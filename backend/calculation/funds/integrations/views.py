"""
This module defines a Api's classes that provides HTTP methods for managing Integrations objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the Integrations model and schema Integrations to work with data.
"""
from calculation.funds.integrations.models import StatementIntegrations
from calculation.funds.integrations.schemas import StatementIntegrationsUpdateSchema, StatementIntegrationsSchema
from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission


class AbstractStatementIntegrationsApi(AbstractViewApi):
    """Define the StatementIntegrationsApi view class for handling HTTP methods related to StatementIntegrations.

    This view class extends the AbstractViewApi class, which provides a basic implementation for common API actions.
    The StatementIntegrationsApi supports HTTP POST and GET methods, and uses the StatementIntegrationsSchema
    serializer for input/output validation. The view requires authenticated users with appropriate permissions to
    access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.
        schema (AutoSchema): An OpenAPI schema object for generating API documentation.
        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/statement_funds/
        ```
    """
    serializer_class = StatementIntegrationsSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = StatementIntegrations
    schema = AutoSchema(tags=["Calculation - Statement Integrations - Extrato de verbas Integratórias"],
                        operation_id_base='Statement Integrations')
    query_params = []


class StatementIntegrationsApi(AbstractStatementIntegrationsApi):
    """Define the StatementIntegrationsApi view class for handling HTTP methods related to StatementIntegrations.

    This view class extends the AbstractViewApi class, which provides a basic implementation for common API actions.
    The StatementIntegrationsApi supports HTTP POST and GET methods, and uses the StatementIntegrationsSchema
    serializer for input/output validation. The view requires authenticated users with appropriate permissions to
    access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.
        schema (AutoSchema): An OpenAPI schema object for generating API documentation.
        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/statement_funds/
        ```
    """
    http_method_names = ['post']


class StatementIntegrationsDetailApi(AbstractStatementIntegrationsApi):
    """Define the StatementIntegrationsApi view class for handling HTTP methods related to StatementIntegrations.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementIntegrationsApi supports HTTP POST and GET methods, and uses the StatementIntegrationsSchema
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
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/statement_funds/
        ```
    """
    serializer_class = StatementIntegrationsUpdateSchema
    http_method_names = ['get', 'put']
    exclude = ('fund_id',)
