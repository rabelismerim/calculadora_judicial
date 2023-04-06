"""
This module defines a Api's classes that provides HTTP methods for managing Irrf objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the Irrf model and schema Irrf to work with data.
"""
from django.http import JsonResponse

from calculation.funds.irrf.models import StatementIRRF, FundIRRF
from calculation.funds.irrf.schemas import StatementIRRFSchema, StatementIRRFUpdateSchema, FundIRRFSchema
from core.abstract.views import AbstractViewApi
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions, status
from core.permission.views import CheckHasPermission


class AbstractFundIRRFApi(AbstractViewApi):
    """Define the FundIRRFApi view class for handling HTTP methods related to FundIRRF.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundIRRFApi supports HTTP POST and GET methods, and uses the FundIRRFSchema
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
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    http_method_names = ['get', 'post']
    serializer_class = FundIRRFSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = FundIRRF
    schema = AutoSchema(tags=["Calculation - Fund IRRF - Verbas IRRF"])

    query_params = [
        {
            "name": "name",
            "field": "name__icontains",
            "in": "query",
            "required": False,
            "description": "Nome da verba",
            "schema": {"type": "string"}
        }
    ]


class FundIRRFApi(AbstractFundIRRFApi):
    """Define the FundIRRFApi view class for handling HTTP methods related to FundIRRF.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundIRRFApi supports HTTP POST and GET methods, and uses the FundIRRFSchema
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
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        """
        Create FundIRRF object from request data and return FundIRRF detail.
        Args:
            request (HttpRequest): HTTP request object containing the POST data.

        Returns:
            JsonResponse: A JSON response containing the created FundIRRF object detail.

        Raises:
            serializers.ValidationError: If the input data is invalid.
            rest_framework.exceptions.PermissionDenied: If the user does not have permission to perform the action.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_funds = serializer.validated_data
        fund = self.model.objects.create(**new_funds)
        return JsonResponse({'fund': self.serializer_class(fund, many=False).data}, status=status.HTTP_201_CREATED)


class FundIRRFDetailApi(AbstractFundIRRFApi):
    """Define the FundIRRFApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundsApi supports HTTP POST and GET methods, and uses the FundsSchema
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
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    http_method_names = ['get', ]


class AbstractStatementIRRFApi(AbstractViewApi):
    """Define the StatementIRRFApi view class for handling HTTP methods related to StatementIRRF.

    This view class extends the AbstractViewApi class, which provides a basic implementation for common API actions.
    The StatementIRRFApi supports HTTP POST and GET methods, and uses the StatementIRRFSchema
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
    serializer_class = StatementIRRFSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = StatementIRRF
    schema = AutoSchema(tags=["Calculation - Statement IRRF - Extrato de verbas IRRF"],
                        operation_id_base='Statement IRRF')
    query_params = []


class StatementIRRFApi(AbstractStatementIRRFApi):
    """Define the StatementIRRFApi view class for handling HTTP methods related to StatementIRRF.

    This view class extends the AbstractViewApi class, which provides a basic implementation for common API actions.
    The StatementIRRFApi supports HTTP POST and GET methods, and uses the StatementIRRFSchema
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


class StatementIRRFDetailApi(AbstractStatementIRRFApi):
    """Define the StatementIRRFApi view class for handling HTTP methods related to StatementIRRF.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementIRRFApi supports HTTP POST and GET methods, and uses the StatementIRRFSchema
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
    serializer_class = StatementIRRFUpdateSchema
    http_method_names = ['get', 'put']
    exclude = ('fund_id',)
