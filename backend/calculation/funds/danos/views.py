"""
This module defines a FundDanosApi class that provides HTTP methods for managing Funds objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The FundDanosApi class uses the Funds model and FundDanosSchema for working with data.
"""
from django.db import transaction
from django.http import JsonResponse
from rest_framework.generics import get_object_or_404

from base.coins.models import Coins
from calculation.funds.danos.models import FundDanos, StatementDanos
from calculation.funds.danos.schemas import FundDanosSchema, FundDanosUpdateSchema, FundDanosGetSchema, \
    TotalValuesDanosDetailSchema, StatementDanosUpdateSchema
from core.abstract.views import AbstractViewApi

from rest_framework import permissions, status
from core.permission.views import CheckHasPermission, CheckHasFundRegisteredPermissions
from utils import _, doc

docs = {
    'init': _("""Represents the values that are used for danos, such as `materiais`, `morais` and
    etc. Contains fields such as `base date`, `value`, `monetary correction` and `economic charges`.
    """)
}


class AbstractFundDanosApi(AbstractViewApi):
    """Define the FundDanosApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundDanosApi supports HTTP POST and GET methods, and uses the FundDanosSchema
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
    serializer_class = FundDanosSchema
    model = FundDanos
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    tags = [_('Cálculo - Verbas - Danos')]
    query_params = [
        {
            "name": "name",
            "field": "name__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Fund name")),
            "schema": {"type": "string"}
        }
    ]


class FundDanosApi(AbstractFundDanosApi):
    """Define the FundDanosApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundDanosApi supports HTTP POST and GET methods, and uses the FundDanosSchema
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
    docs = docs.copy()
    permission_classes = [permissions.IsAuthenticated,
                          CheckHasPermission]
    operation_id_base = 'Detail danos'

    @doc(_("""Create Document Fund object from request data and return Document Fund detail.
        The 'has_custom_fine' field controls whether the fine entered in the document will be used, or the standard 
        fine defined in the calculation
        
    The `commit` parameter is used to control whether a transaction started during the creation of a new object in 
    the database should be committed or not. By default, commit=True, which means that the transaction will be 
    committed automatically when the view's post method has finished executing successfully.
    However, if commit=False, the view will create a new object within a transaction and then immediately roll 
    back, effectively undoing any changes made to the database. This can be useful to get the `calculations`, 
    `results`, `indices`, `corrected value` and etc without saving the information in the database

        :return:
        - JsonResponse: An HTTP response containing the created Funds object detail.

        Raises:
            serializers.ValidationError: If the input data is invalid.
        """))
    def post(self, request, *args, **kwargs):
        commit = request.data.pop('commit', True)
        with transaction.atomic():
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_funds = serializer.validated_data

            statement_danos = new_funds.pop('statement_danos')
            coins = new_funds.get('coins')
            new_funds['coins'] = Coins.objects.create(**coins)
            fund = self.model.objects.create(**new_funds)
            statement_danos['fund'] = fund
            StatementDanos.objects.create(**statement_danos)
            if commit is False:
                transaction.set_rollback(True)
        if commit is False:
            transaction.rollback()
        return JsonResponse({'fund_danos': self.serializer_class(fund, many=False).data},
                            status=status.HTTP_201_CREATED)


class FundDanosDetailApi(AbstractFundDanosApi):
    """Define the FundDanosApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundDanosApi supports HTTP POST and GET methods, and uses the FundDanosSchema
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
    docs = docs.copy()
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    docs['get'] = _("""This method handles GET requests for the view. It retrieves a specific document fund object 
    using the given  id from the query parameters and serializes the result into JSON format before returning it as an 
        HTTP response. 

            :return:
                JsonResponse: An HTTP response containing the serialized document fund data retrieved.
            """)
    http_method_names = ['get', 'put', 'delete']

    layout_serializers = {
        'default': FundDanosSchema,
        'get': FundDanosGetSchema,
        'put': FundDanosUpdateSchema,
    }

    @doc(_("""This method handles PUT requests for the view. It updates a specific document fund object using the given id 
    from the query parameters and the serialized input data from the request body. 
    
        :return:
            - JsonResponse: An HTTP response containing the serialized document fund data updated.
            """))
    def put(self, request, *args, **kwargs):
        id_ = kwargs.get('id')
        serializer = self.get_serializer_class()
        serializer = serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data_obj = dict(serializer.validated_data)
        document = get_object_or_404(self.model, id=id_)
        statement_danos = data_obj.pop('statement_danos', None)

        if statement_danos:
            statement = document.statementdanos
            statement.dict_update(**statement_danos)
        document.dict_update(**data_obj)
        return JsonResponse({'fund_danos': self.serializer_class(document, many=False).data})

    @doc(_("""Delete a specific statement danos according to the ID passed by the url

                        :return:
                            JsonResponse: A JSON response containing the ok message.
                        """))
    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            fund_id = kwargs.get('id')
            document = get_object_or_404(FundDanos, id=fund_id)
            document.delete()
        return JsonResponse({'data': _('Statement fund deleted')}, status=status.HTTP_200_OK)


class StatementFundsDanosListApi(AbstractFundDanosApi):
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
    serializer_class = TotalValuesDanosDetailSchema
    http_method_names = ['get', 'put']
    docs = docs.copy()
    model = FundDanos

    layout_serializers = {
        'default': TotalValuesDanosDetailSchema,
        'get': TotalValuesDanosDetailSchema,
        'put': StatementDanosUpdateSchema,
    }

    tags = [_('Cálculo - Verbas - Danos - Valores das verbas')]

    @doc(_("""This method handles GET requests for the view. It retrieves the calculated fund total and a list of fund 
    IRRF objects using the received fund_id from the query parameters and serializes the result into 
    JSON format before returning it as an JSON response. 

    :return:
        - JsonResponse: An HTTP response containing the serialized statement IRRF data retrieved.
    """))
    def get(self, request, *args, **kwargs):
        funds_data = self.get_total_response(request, *args, **kwargs)
        return JsonResponse({'fund': funds_data})

    def get_total_response(self, request, *args, **kwargs):
        fund_id = kwargs.get('fund_id')
        fund = self.model.objects.filter(id=fund_id).first()
        if hasattr(fund, 'totalvaluesdanos'):
            funds_data = self.serializer_class(
                fund.totalvaluesdanos, many=False).data
        else:
            funds_data = self.serializer_class(fund, many=False).data
        return funds_data

    def put(self, request, *args, **kwargs):
        """
        This method handles PUT requests for the view. It expects input data that conform to the serializer used by
        the view class. It updates the approved_calculation or date object of a specific comparative object using the
        given calculation_id from the query parameters and serializes the updated object in JSON format before
        returning it as an HTTP response.

        :params:
            request: The HTTP request object. args: Any additional positional arguments passed to the method.
            kwargs: Any additional keyword arguments passed to the method, with calculation_id identifying the
            comparative object to update. :return: JsonResponse: An HTTP response containing the updated and serialized
            comparative object data.
        """
        with transaction.atomic():
            id_ = kwargs.get('fund_id')
            serializer = self.get_serializer_class()

            serializer = serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data_obj = serializer.validated_data

            fund_fields = ['interest_initial_date', 'apply_monetary_correction', 'type_interest']
            fund_items = {}
            for item in fund_fields:
                item_value = data_obj.pop(item, None)
                if item_value:
                    fund_items[item] = item_value
            obj = get_object_or_404(StatementDanos, fund_id=id_)
            fund = obj.fund
            fund.dict_update(**fund_items)
            obj.dict_update(**data_obj)
        funds_data = self.get_total_response(request, *args, **kwargs)
        return JsonResponse({'fund': funds_data.get('data')[0]})
