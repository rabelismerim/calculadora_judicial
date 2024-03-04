"""
This module defines a FundDeductionApi class that provides HTTP methods for managing Funds objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The FundDeductionApi class uses the Funds model and FundDeductionSchema for working with data.
"""
from django.db import transaction
from django.http import JsonResponse
from rest_framework.generics import get_object_or_404

from base.coins.models import Coins
from calculation.funds.deduction.models import FundDeduction, StatementDeduction
from calculation.funds.deduction.schemas import FundDeductionSchema, StatementDeductionSchema, \
    TotalStatementDeductionSchema
from calculation.funds.schemas import StatementFundsUpdateSchema
from core.abstract.views import AbstractViewApi

from rest_framework import permissions, status
from core.permission.views import CheckHasPermission, CheckFundsPjPfPermissions, CheckHasFundRegisteredPermissions
from utils import _, doc

docs = {
    'init': _("""Represents the values that are used for documents, such as `invoices`, `Indemnities`, `agreements`, 
    etc. Contains fields such as `base date`, `value`, `monetary correction` and `economic charges`.
    """)
}


class AbstractFundDeductionApi(AbstractViewApi):
    """Define the FundDeductionApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundDeductionApi supports HTTP POST and GET methods, and uses the FundDeductionSchema
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
    serializer_class = FundDeductionSchema
    model = FundDeduction
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    tags = [_('Cálculo - Verbas - Dedução')]
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


class FundDeductionApi(AbstractFundDeductionApi):
    """Define the FundDeductionApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundDeductionApi supports HTTP POST and GET methods, and uses the FundDeductionSchema
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
                          CheckHasPermission, CheckHasFundRegisteredPermissions]

    serializer_class = StatementDeductionSchema

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
            fund = StatementDeduction.objects.create(**new_funds)
            if commit is False:
                transaction.set_rollback(True)
        if commit is False:
            transaction.rollback()
        return JsonResponse({'fund_deduction': self.serializer_class(fund, many=False).data},
                            status=status.HTTP_201_CREATED)


class FundDeductionDetailApi(AbstractFundDeductionApi):
    """Define the FundDeductionApi view class for handling HTTP methods related to Funds.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The FundDeductionApi supports HTTP POST and GET methods, and uses the FundDeductionSchema
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
        'default': FundDeductionSchema,
        # 'get': FundDeductionGetSchema,
        # 'put': FundDeductionUpdateSchema,
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
        statement_document = data_obj.pop('statement_document', None)

        if statement_document:
            statement = document.statementdocument
            statement.dict_update(**statement_document)
        document.dict_update(**data_obj)
        return JsonResponse({'fund_document': self.serializer_class(document, many=False).data})

    @doc(_("""Delete a specific statement document according to the ID passed by the url

                        :return:
                            JsonResponse: A JSON response containing the ok message.
                        """))
    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            fund_id = kwargs.get('id')
            document = get_object_or_404(FundDeduction, id=fund_id)
            document.delete()
        return JsonResponse({'data': _('Statement fund deleted')}, status=status.HTTP_200_OK)


class StatementFundsDeductionDetailApi(AbstractViewApi):
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
    serializer_class = StatementDeductionSchema
    http_method_names = ['get', 'put', 'delete']
    model = StatementDeduction

    docs = docs.copy()
    docs['get'] = _("""This method handles GET requests for the view. It retrieves a specific statement fund object 
    using the given id from the query parameters and serializes the result into JSON format before returning it as an 
    HTTP response. 

            :return:
                JsonResponse: An HTTP response containing the serialized statement fund data retrieved.
        """)
    docs['put'] = _("""This method handles PUT requests for the view. It updates a specific statement fund 
        object using the given id from the query parameters and the serialized input data from the request body. 

            :return:
                JsonResponse: An HTTP response containing the serialized statement fund data updated.
                """)

    docs['delete'] = _("""Delete a specific statement fund according to the ID passed by the url

            :return:
                - JsonResponse: An HTTP response containing the ok message.
            """)

    def get(self, request, *args, **kwargs):
        fund_id = kwargs.get('id')
        fund = FundDeduction.objects.filter(id=fund_id).first()
        funds_data = TotalStatementDeductionSchema(fund, many=False).data
        return JsonResponse({'fund': funds_data})

    def put(self, request, *args, **kwargs):
        fund_id = kwargs.get('id')
        fund = FundDeduction.objects.filter(statementdeduction__id=fund_id).first()
        fund.statementdeduction_set.all().update(used_remaining_balance=False)
        return super().put(request, *args, **kwargs)
