"""
This module defines a StatementApi class that provides HTTP methods for managing Statement objects.
It extends the AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
The API responds with JSON data and utilizes the rest_framework.schemas.openapi.AutoSchema for generating API documentation.
The StatementApi class uses the Statement model and StatementSchema for working with data.
"""
from django.http import JsonResponse

from calculation.statement.schemas import StatementSchema
from calculation.statement.models import Statement
from core.abstract.views import AbstractViewApi
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _, doc


class StatementApi(AbstractViewApi):
    """Define the StatementApi view class for handling HTTP methods related to Statement.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The StatementApi supports HTTP POST and GET methods, and uses the StatementSchema
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
        To retrieve statement with a matching description:
        ```
        GET /api/v1/statement/?statement=statement_name
        ```
    """
    http_method_names = ['get']
    serializer_class = StatementSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Statement
    schema = AutoSchema(tags=[str(_("Calculation - Statement"))])
    docs = {
        'init': _("""Represents the entire extract of the calculation. All results of `calculations`, `fines`, 
        `amounts due`, `claims`, `summary of funds`, `DTT opinion`, `classes` and `used assumptions`.
        """)
    }
    query_params = []

    @doc("""This method handles GET requests for the view. It retrieves a specific statement object using the given 
        calculation_id from the query parameters and serializes the result into JSON format before returning it as an 
        HTTP response. 

            Returns:
                JsonResponse: An HTTP response containing the serialized statement data retrieved.
            """)
    def get(self, request, *args, **kwargs):
        calculation_id = kwargs.get('calculation_id')
        statement = self.model.objects.filter(
            calculation_id=calculation_id).first()
        statement_data = self.serializer_class(statement, many=False).data
        return JsonResponse({'statement': statement_data})
