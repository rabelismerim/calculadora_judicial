"""
This module defines a StatementPJApi class that provides HTTP methods for managing Statement_Pj objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The StatementPJApi class uses the Statement_Pj model and Statement_PjSchema for working with data.
"""
from compat import JsonResponse

from core.abstract.views import AbstractViewApi

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from calculation.statement_pj.models import StatementPJ
from calculation.statement_pj.schemas import StatementPJSchema
from utils import doc, _


class StatementPJApi(AbstractViewApi):
    """Define the StatementPJApi view class for handling HTTP methods related to StatementPJ.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementPJApi supports HTTP POST and GET methods, and uses the StatementPJSchema
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
        To retrieve statement_pj with a matching description:
        ```
        GET /api/v1/statement_pj/?statement_pj=statement_pj_name
        ```
    """
    http_method_names = ['get']
    serializer_class = StatementPJSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = StatementPJ

    docs = {
        'init': _("""Represents the entire extract from the calculation of the truths of legal entities. All results 
        of `calculations`, `fines`, `amounts due`, `claims`, `summary of funds`, `DTT opinion`, `classes` and 
        `used assumptions`.
            """),
    }

    query_params = []

    @doc("""This method handles GET requests for the view. It retrieves a specific statement PJ object using the given 
            calculation_id from the query parameters and serializes the result into JSON format before returning it as
             an  HTTP response. 

                Returns:
                    JsonResponse: An HTTP response containing the serialized statement PJ data retrieved.
                """)
    def get(self, request, *args, **kwargs):
        calculation_id = kwargs.get('calculation_id')
        statement = self.model.objects.filter(
            statement__calculation_id=calculation_id).first()
        statement_data = self.serializer_class(statement, many=False).data
        return JsonResponse({'statement_pj': statement_data})
