"""
This module defines a FundDocumentApi class that provides HTTP methods for managing Funds objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The FundDocumentApi class uses the Funds model and FundDocumentSchema for working with data.
"""

from django.http import JsonResponse

from calculation.funds.document.models import FundDocument, StatementDocument
from calculation.funds.document.schemas import FundDocumentSchema, StatementDocumentSchema, \
    StatementFundDocumentUpdateSchema
from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions, status
from core.permission.views import CheckHasPermission


class AbstractFundDocumentApi(AbstractViewApi):
    """Define the FundDocumentApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundDocumentApi supports HTTP POST and GET methods, and uses the FundDocumentSchema
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
    serializer_class = FundDocumentSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = FundDocument
    schema = AutoSchema(
        tags=["Calculation - Fund Document - Verbas documentos"])

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


class FundDocumentApi(AbstractFundDocumentApi):
    """Define the FundDocumentApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundDocumentApi supports HTTP POST and GET methods, and uses the FundDocumentSchema
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
        Create Funds object from request data and return Funds detail.
        Args:
            request (HttpRequest): HTTP request object containing the POST data.

        Returns:
            JsonResponse: A JSON response containing the created Funds object detail.

        Raises:
            serializers.ValidationError: If the input data is invalid.
            rest_framework.exceptions.PermissionDenied: If the user does not have permission to perform the action.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_funds = serializer.validated_data
        statement_document = new_funds.pop('statement_document')
        fund = self.model.objects.create(**new_funds)
        statement_document['fund'] = fund
        StatementDocument.objects.create(**statement_document)
        return JsonResponse({'fund_document': self.serializer_class(fund, many=False).data}, status=status.HTTP_201_CREATED)


class FundDocumentDetailApi(AbstractFundDocumentApi):
    """Define the FundDocumentApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundDocumentApi supports HTTP POST and GET methods, and uses the FundDocumentSchema
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


class AbstractStatementFundDocumentApi(AbstractViewApi):
    """Define the StatementFundDocumentApi view class for handling HTTP methods related to StatementFunds.

    This view class extends the AbstractViewApi class, which provides a basic implementation for common API actions.
    The StatementFundDocumentApi supports HTTP POST and GET methods, and uses the StatementFundDocumentSchema
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
        GET /api/v1/calculation/funds/funds/
        ```
    """
    serializer_class = StatementDocumentSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = StatementDocument
    schema = AutoSchema(tags=["Calculation - Statement Funds Documents - Extrato de verbas documentos"],
                        operation_id_base='Statement Funds Documents')
    query_params = []


class StatementFundDocumentApi(AbstractStatementFundDocumentApi):
    """Define the StatementFundDocumentApi view class for handling HTTP methods related to StatementFunds.

    This view class extends the AbstractViewApi class, which provides a basic implementation for common API actions.
    The StatementFundDocumentApi supports HTTP POST and GET methods, and uses the StatementFundDocumentSchema
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
        GET /api/v1/calculation/funds/funds/
        ```
    """
    http_method_names = ['post']


class StatementFundDocumentDetailApi(AbstractStatementFundDocumentApi):
    """Define the StatementFundDocumentApi view class for handling HTTP methods related to StatementFunds.

    This view class extends the AbstractViewApi class, which provides a basic implementation for common API actions.
    The StatementFundDocumentApi supports HTTP POST and GET methods, and uses the StatementFundDocumentSchema
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
        GET /api/v1/calculation/funds/funds/
        ```
    """
    serializer_class = StatementFundDocumentUpdateSchema
    http_method_names = ['get', 'put']
