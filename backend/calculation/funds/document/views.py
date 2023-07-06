"""
This module defines a FundDocumentApi class that provides HTTP methods for managing Funds objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The FundDocumentApi class uses the Funds model and FundDocumentSchema for working with data.
"""
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.generics import get_object_or_404

from base.coins.models import Coins
from calculation.funds.document.models import FundDocument, StatementDocument
from calculation.funds.document.schemas import FundDocumentSchema, FundDocumentUpdateSchema, FundDocumentGetSchema, \
    TotalValuesDocumentSchema, TotalValuesDocumentDetailSchema, StatementDocumentUpdateSchema
from core.abstract.views import AbstractViewApi

from rest_framework import permissions, status
from core.permission.views import CheckHasPermission, CheckFundsPjPfPermissions, CheckHasFundRegisteredPermissions
from utils import _, doc

docs = {
    'init': _("""Represents the values that are used for documents, such as `invoices`, `Indemnities`, `agreements`, 
    etc. Contains fields such as `base date`, `value`, `monetary correction` and `economic charges`.
    """)
}


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

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    serializer_class = FundDocumentSchema
    model = FundDocument
    tags = [_('Cálculo - Verbas - Documentos')]
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

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve funds with a matching description:
        ```
        GET /api/v1/calculation/funds/?funds=funds_name
        ```
    """
    http_method_names = ['post']
    docs = docs.copy()
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission, CheckHasFundRegisteredPermissions]

    @doc(_("""Create Document Fund object from request data and return Document Fund detail.
        The 'has_custom_fine' field controls whether the fine entered in the document will be used, or the standard 
        fine defined in the calculation
        
    The `commit` parameter is used to control whether a transaction started during the creation of a new object in 
    the database should be committed or not. By default, commit=True, which means that the transaction will be 
    committed automatically when the view's post method has finished executing successfully.
    However, if commit=False, the view will create a new object within a transaction and then immediately roll 
    back, effectively undoing any changes made to the database. This can be useful to get the `calculations`, 
    `results`, `indices`, `corrected value` and etc without saving the information in the database

        Returns:
            JsonResponse: A JSON response containing the created Funds object detail.

        Raises:
            serializers.ValidationError: If the input data is invalid.
        """))
    def post(self, request, *args, **kwargs):
        commit = request.data.pop('commit', True)
        with transaction.atomic():
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            new_funds = serializer.validated_data
            statement_document = new_funds.pop('statement_document')
            coins = new_funds.get('coins')
            new_funds['coins'] = Coins.objects.create(**coins)
            fund = self.model.objects.create(**new_funds)
            statement_document['fund'] = fund
            StatementDocument.objects.create(**statement_document)
            if commit is False:
                transaction.set_rollback(True)
        if commit is False:
            transaction.rollback()

        return JsonResponse({'fund_document': self.serializer_class(fund, many=False).data},
                            status=status.HTTP_201_CREATED)


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

            Returns:
                JsonResponse: An HTTP response containing the serialized document fund data retrieved.
            """)
    http_method_names = ['get', 'put', 'delete']

    layout_serializers = {
        'default': FundDocumentSchema,
        'get': FundDocumentGetSchema,
        'put': FundDocumentUpdateSchema,
    }

    @doc(_("""This method handles PUT requests for the view. It updates a specific document fund object using the given id 
    from the query parameters and the serialized input data from the request body. 
    
        Returns:
            JsonResponse: An HTTP response containing the serialized document fund data updated.
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

                        Returns:
                            JsonResponse: A JSON response containing the ok message.
                        """))
    def delete(self, request, *args, **kwargs):
        fund_id = kwargs.get('id')
        statement = get_object_or_404(StatementDocument, fund_id=fund_id)
        statement.delete()
        return JsonResponse({'data': _('Statement fund deleted')}, status=status.HTTP_200_OK)


class StatementFundsIRRFListApi(AbstractFundDocumentApi):
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
    serializer_class = TotalValuesDocumentDetailSchema
    http_method_names = ['get', 'put']
    docs = docs.copy()
    model = FundDocument

    layout_serializers = {
        'default': TotalValuesDocumentDetailSchema,
        'get': TotalValuesDocumentDetailSchema,
        'put': StatementDocumentUpdateSchema,
    }

    tags = [_('Cálculo - Verbas - Documentos - Valores das verbas')]

    @doc(_("""This method handles GET requests for the view. It retrieves the calculated fund total and a list of fund 
    IRRF objects using the received fund_id from the query parameters and serializes the result into 
    JSON format before returning it as an JSON response. 

    Returns:
        JsonResponse: An HTTP response containing the serialized statement IRRF data retrieved.
    """))
    def get(self, request, *args, **kwargs):
        fund_id = kwargs.get('fund_id')
        fund = self.model.objects.filter(id=fund_id).first()
        if hasattr(fund, 'totalvaluesdocument'):
            funds_data = self.serializer_class(fund.totalvaluesdocument, many=False).data
        else:
            funds_data = self.serializer_class(fund, many=False).data
        return JsonResponse({'fund': funds_data})

    def put(self, request, *args, **kwargs):
        """
        This method handles PUT requests for the view. It expects input data that conform to the serializer used by
        the view class. It updates the approved_calculation or date object of a specific comparative object using the
        given calculation_id from the query parameters and serializes the updated object in JSON format before
        returning it as an HTTP response.

        Parameters: request: The HTTP request object. args: Any additional positional arguments passed to the method.
        kwargs: Any additional keyword arguments passed to the method, with calculation_id identifying the
        comparative object to update. Returns: JsonResponse: An HTTP response containing the updated and serialized
        comparative object data.
        """
        with transaction.atomic():
            id_ = kwargs.get('fund_id')
            serializer = self.get_serializer_class()
            serializer = serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data_obj = dict(serializer.validated_data)
            obj = get_object_or_404(StatementDocument, fund_id=id_)
            obj.dict_update(**data_obj)
        return JsonResponse({self.get_model_name(): self.serializer_class(obj, many=False).data})
