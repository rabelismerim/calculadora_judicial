"""
This module defines a Api's classes that provides HTTP methods for managing Integrations objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the Integrations model and schema Integrations to work with data.
"""
from django.http import JsonResponse
from rest_framework.generics import get_object_or_404

from calculation.funds.integrations.models import StatementIntegrations
from calculation.funds.integrations.schemas import StatementIntegrationsUpdateSchema, StatementIntegrationsSchema, \
    TotalValuesFundsIntegrationsSchema
from calculation.funds.models import Funds
from core.abstract.views import AbstractViewApi

from rest_framework import permissions, status
from core.permission.views import CheckHasPermission
from utils import _, doc

docs = {
    'init': _("""Statement Integrations is a financial statement of a fund, and includes attributes such as 
    `base date` and `historical value`. It also has the calculation, `monetary correction` and the `indexes` used in the 
    calculations. It has a relationship with a fund where this fund can n Statement Integrations.
    """)
}


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
    query_params = []
    tags = [_('Cálculo - Valores da Verba - Integratórias')]


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

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/statement_funds/
        ```
    """
    docs = docs.copy()
    docs['post'] = _("""Create Statement Integration object from request data and return Statement Integration detail.
        Returns:
            JsonResponse: A JSON response containing the created Funds
             object detail.

        Raises:
            serializers.ValidationError: If the input data is invalid.
            """)
    http_method_names = ['post']


class StatementIntegrationsDetailApi(AbstractStatementIntegrationsApi):
    """Define the StatementIntegrationsApi view class for handling HTTP methods related to StatementIntegrations.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementIntegrationsApi supports HTTP POST and GET methods, and uses the
    StatementIntegrationsSchema
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
    serializer_class = StatementIntegrationsUpdateSchema
    http_method_names = ['get', 'put', 'delete']
    exclude = ('fund_id',)
    docs = docs.copy()
    docs['get'] = _("""This method handles GET requests for the view. It retrieves a specific statement integration 
    object using the given id from the query parameters and serializes the result into JSON format before returning it
     as an HTTP response. 
     
        Returns:
            JsonResponse: An HTTP response containing the serialized document fund data retrieved.
    """)
    docs['put'] = _("""This method handles PUT requests for the view. It updates a specific statement integration 
    object using the given id from the query parameters and the serialized input data from the request body. 
    
        Returns:
            JsonResponse: An HTTP response containing the serialized statement integration data updated.
            """)

    @doc(_("""Delete a specific statement integrations according to the ID passed by the url

                Returns:
                    JsonResponse: A JSON response containing the ok message.
                """))
    def delete(self, request, *args, **kwargs):
        statement_id = kwargs.get('id')
        statement = get_object_or_404(StatementIntegrations, id=statement_id)
        statement.delete()
        return JsonResponse({'data': _('Statement fund deleted')}, status=status.HTTP_200_OK)


class StatementFundsIntegrationListApi(AbstractStatementIntegrationsApi):
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
        GET /api/v1/calculation/funds/labor/integration/<uuid:fund_id>/
        ```
    """
    serializer_class = TotalValuesFundsIntegrationsSchema
    http_method_names = ['get']
    docs = docs.copy()
    model = Funds

    @doc(_("""This method handles GET requests for the view. It retrieves the calculated fund total and a list of fund 
    statement integrations objects using the received fund_id from the query parameters and serializes the result into 
    JSON format before returning it as an JSON response. 

    Returns:
        JsonResponse: An HTTP response containing the serialized statements data retrieved.
    """))
    def get(self, request, *args, **kwargs):
        fund_id = kwargs.get('fund_id')
        fund = self.model.objects.filter(id=fund_id).first()
        if hasattr(fund, 'totalvaluesfundsintegrations'):
            funds_data = self.serializer_class(fund.totalvaluesfunds, many=False).data
        else:
            funds_data = self.serializer_class(fund, many=False).data
        return JsonResponse({'fund': funds_data})
