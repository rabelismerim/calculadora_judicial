"""
This module defines a FundsApi class that provides HTTP methods for managing Funds objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The FundsApi class uses the Funds model and FundsSchema for working with data.
"""


from django.http import JsonResponse
from calculation.funds.schemas import FundsSchema
from calculation.funds.models import Funds, StatementFunds, StatementIRRF, StatementIntegrations
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

        fund = CreateFunds(new_funds).create_funds()
        return JsonResponse({'funds': self.serializer_class(fund, many=False).data}, status=status.HTTP_201_CREATED)


class CreateFunds:
    """Helper class for creating Funds objects from validated data.

    This class creates a Funds object from a validated dictionary of input data. The object is
    created by first creating the parent Funds object, and then creating any associated child
    objects (StatementFunds, StatementIntegrations, and StatementIRRF) if provided.

    Attributes:
        funds (dict): A dictionary containing the validated input data for the Funds object.
        calculation_id (int): An optional integer representing the ID of the associated calculation.

    Methods:
        create_funds: Create a Funds object from the input data and return the created object.

    """

    def __init__(self, funds, calculation_id=None):
        """
        Initialize the CreateFunds object with the validated input data and an optional
        calculation ID.

        Args:
            funds (dict): A dictionary containing the validated input data for the Funds object.
            calculation_id (uuid): An optional integer representing the UUID of the associated calculation.
        """
        self.funds = funds
        if calculation_id:
            self.funds['calculation_id'] = calculation_id

    def create_funds(self) -> Funds:
        """
        Create Funds object with the validated input data.

        Returns:
            Funds: A Funds object detail.
        """
        new_funds = self.funds
        new_statement_irrfs = new_funds.pop('statement_irrf', [])
        new_statement_funds = new_funds.pop('statement_funds', [])
        new_statement_integrations = new_funds.pop(
            'statement_integrations', [])

        fund = Funds.objects.create(**new_funds)

        for statement_fund in new_statement_funds:
            StatementFunds.objects.create(fund=fund, **statement_fund)

        for statement_integration in new_statement_integrations:
            StatementIntegrations.objects.create(
                fund=fund, **statement_integration)

        for statement_irrf in new_statement_irrfs:
            StatementIRRF.objects.create(
                fund=fund, **statement_irrf)

        return fund
