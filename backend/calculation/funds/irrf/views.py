"""
This module defines a Api's classes that provides HTTP methods for managing Irrf objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the Irrf model and schema Irrf to work with data.
"""
from django.http import JsonResponse

from base.coins.models import Coins
from calculation.funds.irrf.models import StatementIRRF, FundIRRF
from calculation.funds.irrf.schemas import StatementIRRFSchema, StatementIRRFUpdateSchema, FundIRRFSchema
from core.abstract.views import AbstractViewApi

from rest_framework import permissions, status
from core.permission.views import CheckHasPermission, CheckFundsPjPfPermissions, CheckHasAgreementRegisteredPermissions
from utils import _, doc

docs = {
    'init': _("""Statement IRRF is a financial statement of a fund IRRF, and includes attributes such as 
    `fund_name` and `taxable_amounts`. It also has the calculation, `taxable amount` and the `taxable portion` used in 
    the calculations. It has a relationship with a fund IRRF where this fund can n Statement IRRF.
    """)
}

docs_fund = {
    'init': _("""Represent a template for IRRF funds. He has the attributes `taxable_amount` and `months_period`, 
    which represent the taxable amount of the fund and the number of months of the application period, respectively. 
    It has a 1 to n relationship, where several amounts and their respective values can be allocated, to calculate 
    the IRRF due, returning fields such as: `tax amount`, `taxable portion` and `aliquot`.
    """)
}


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

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    serializer_class = FundIRRFSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission, CheckFundsPjPfPermissions,
                          CheckHasAgreementRegisteredPermissions]
    physical_person = True
    model = FundIRRF
    query_params = []


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

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    docs = docs_fund.copy()
    http_method_names = ['post']

    @doc(_("""Create FundIRRF object from request data and return FundIRRF detail.
        Args:
            request (HttpRequest): HTTP request object containing the POST data.

        Returns:
            JsonResponse: A JSON response containing the created FundIRRF object detail.

        Raises:
            serializers.ValidationError: If the input data is invalid.
        """))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_funds = serializer.validated_data
        coins = new_funds.get('coins')
        new_funds['coins'] = Coins.objects.create(**coins)
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

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    http_method_names = ['get', ]
    docs = docs_fund.copy()
    docs['get'] = _("""This method handles GET requests for the view. It retrieves a specific fund IRRF 
        object using the given id from the query parameters and serializes the result into JSON format before returning
         it as an HTTP response. 

            Returns:
                JsonResponse: An HTTP response containing the serialized document fund data retrieved.
        """)


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

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/statement_funds/
        ```
    """
    http_method_names = ['post']
    docs = docs.copy()
    docs['post'] = _("""Create Statement IRRF object from request data and return Statement IRRF detail.
        Returns:
            JsonResponse: A JSON response containing the created Funds
             object detail.

        Raises:
            serializers.ValidationError: If the input data is invalid.
            """)


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
    docs = docs.copy()
    docs['get'] = _("""This method handles GET requests for the view. It retrieves a specific statement IRRF 
        object using the given id from the query parameters and serializes the result into JSON format before returning
         it as an HTTP response. 

            Returns:
                JsonResponse: An HTTP response containing the serialized document fund data retrieved.
        """)
    docs['put'] = _("""This method handles PUT requests for the view. It updates a specific statement IRRF 
        object using the given id from the query parameters and the serialized input data from the request body. 

            Returns:
                JsonResponse: An HTTP response containing the serialized statement IRRF data updated.
                """)
