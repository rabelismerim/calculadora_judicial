"""
This module defines a FundsApi class that provides HTTP methods for managing Funds objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The FundsApi class uses the Funds model and FundsSchema for working with data.
"""

from django.http import JsonResponse

from base.coins.models import Coins
from calculation.funds.schemas import FundsSchema, StatementFundsSchema, StatementFundsUpdateSchema
from calculation.funds.models import Funds, StatementFunds
from core.abstract.views import AbstractViewApi

from rest_framework import permissions, status
from core.permission.views import CheckHasPermission
from utils import _, doc

docs = {
    'init': _("""Statement Fund is a financial statement of a fund, and includes attributes such as 
    `base date` and `historical value`. It also has the calculation, `monetary correction` and the `indexes` used in the 
    calculations. It has a relationship with a fund where this fund can n Statement Fund.
    """)
}

docs_fund = {
    'init': _("""Represents a template for funds. It has the attributes `name` and `calculated total values`,
    that represent the values that were inserted in the extracts.
    It has a ratio of 1 to n for the statement funds and statement funds integrations, where several values and their 
    respective values can be allocated to calculate the corrections.
    """)
}


class AbstractFundsApi(AbstractViewApi):
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
        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    serializer_class = FundsSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Funds

    query_params = []


class FundsApi(AbstractFundsApi):
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
        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    http_method_names = ['post']
    docs = docs_fund.copy()

    @doc(_("""Create Funds object from request data and return Funds detail.
        Args:
            request (HttpRequest): HTTP request object containing the POST data.

        Returns:
            JsonResponse: A JSON response containing the created Funds object detail.

        Raises:
            serializers.ValidationError: If the input data is invalid.
            rest_framework.exceptions.PermissionDenied: If the user does not have permission to perform the action.
        """))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_funds = serializer.validated_data
        fund = CreateFunds(new_funds).create_funds()
        return JsonResponse({'funds': self.serializer_class(fund, many=False).data}, status=status.HTTP_201_CREATED)


class FundsDetailApi(AbstractFundsApi):
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

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    http_method_names = ['get', ]
    docs = docs_fund.copy()
    docs['get'] = _("""This method handles GET requests for the view. It retrieves a specific fund 
        object using the given id from the query parameters and serializes the result into JSON format before returning it
         as an HTTP response. 

            Returns:
                JsonResponse: An HTTP response containing the serialized fund data retrieved.
        """)


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
        coins = new_funds.get('coins')
        new_funds['coins'] = Coins.objects.create(**coins)
        fund = Funds.objects.create(**new_funds)
        return fund


class AbstractStatementFundsApi(AbstractViewApi):
    """Define the StatementFundsApi view class for handling HTTP methods related to StatementFunds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementFundsApi supports HTTP POST and GET methods, and uses the StatementFundsSchema
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
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/funds/
        ```
    """
    serializer_class = StatementFundsSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = StatementFunds
    query_params = []


class StatementFundsApi(AbstractStatementFundsApi):
    """Define the StatementFundsApi view class for handling HTTP methods related to StatementFunds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementFundsApi supports HTTP POST and GET methods, and uses the StatementFundsSchema
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
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/funds/
        ```
    """
    http_method_names = ['post']
    docs = docs.copy()
    docs['post'] = _("""Create Statement Fund object from request data and return Statement Fund detail.
            Returns:
                JsonResponse: A JSON response containing the created Funds
                 object detail.

            Raises:
                serializers.ValidationError: If the input data is invalid.
                """)


class StatementFundsDetailApi(AbstractStatementFundsApi):
    """Define the StatementFundsApi view class for handling HTTP methods related to StatementFunds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementFundsApi supports HTTP POST and GET methods, and uses the StatementFundsSchema
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
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/funds/
        ```
    """
    serializer_class = StatementFundsUpdateSchema
    http_method_names = ['get', 'put']
    docs = docs.copy()
    docs['get'] = _("""This method handles GET requests for the view. It retrieves a specific statement fund object 
    using the given id from the query parameters and serializes the result into JSON format before returning it as an 
    HTTP response. 

            Returns:
                JsonResponse: An HTTP response containing the serialized statement fund data retrieved.
        """)
    docs['put'] = _("""This method handles PUT requests for the view. It updates a specific statement fund 
        object using the given id from the query parameters and the serialized input data from the request body. 

            Returns:
                JsonResponse: An HTTP response containing the serialized statement fund data updated.
                """)
