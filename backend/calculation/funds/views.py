"""
This module defines a FundsApi class that provides HTTP methods for managing Funds objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The FundsApi class uses the Funds model and FundsSchema for working with data.
"""


from django.http import JsonResponse
from calculation.funds.schemas import FundsSchema
from calculation.funds.models import Funds, StatementFunds, StatementIntegrations
from core.abstract.views import AbstractViewApi
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions, status
from core.permission.views import CheckHasPermission


class FundsApi(AbstractViewApi):
    """Define the FundsApi view class for handling HTTP methods related to Funds.

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
    http_method_names = ['get', 'post']
    serializer_class = FundsSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Funds
    schema = AutoSchema(tags=["Calculation - Funds"])

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

    def post(self, request, *args, **kwargs):
        """
           Create Funds receiving a dict, return Funds detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_funds = serializer.validated_data
        new_statement_funds = new_funds.pop('statement_funds', [])
        new_statement_integrations = new_funds.pop(
            'statement_integrations', [])

        fund = self.model.objects.create(**new_funds)

        for statement_fund in new_statement_funds:
            StatementFunds.objects.create(fund=fund, **statement_fund)

        for statement_integration in new_statement_integrations:
            StatementIntegrations.objects.create(
                fund=fund, **statement_integration)

        return JsonResponse({'funds': self.serializer_class(fund, many=False).data}, status=status.HTTP_201_CREATED)
