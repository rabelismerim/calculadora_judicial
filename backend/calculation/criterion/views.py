from django.http import JsonResponse

from calculation.criterion.models import Criterion
from calculation.criterion.schemas import CriterionSchema
from core.abstract.views import AbstractViewApi
from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _, doc


class CriterionApi(AbstractViewApi):
    """Define the CriterionApi view class for handling HTTP methods related to criterion.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CriterionApi supports HTTP POST and GET methods, and uses the CriterionSchema
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
        To retrieve criterion with a matching description:
        ```
        GET /api/v1/criterion/?sentenca=sentenca_name
        ```
    """
    http_method_names = ['get']
    serializer_class = CriterionSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Criterion
    tags=[_("Calculation - Criterion")]

    query_params = []

    docs = {
        'init': _("""Represents the amounts used as assumptions for the calculation at the time it was requested, 
        to maintain the values in case there are changes later in the creditor, recovering or in the assumptions of the 
        calculation. It has values such as `date of RJ's request`, `claims`, `fines` and `interest`.
        """)
    }

    @doc("""This method handles GET requests for the view. It retrieves a specific criterion object using the given 
        calculation_id from the query parameters and serializes the result into JSON format before returning it as an 
        HTTP response. 

            Returns:
                JsonResponse: An HTTP response containing the serialized comparative data retrieved.
            """)
    def get(self, request, *args, **kwargs):
        calculation_id = kwargs.get('calculation_id')
        criterion = self.model.objects.filter(calculation_id=calculation_id).first()
        criterion_data = self.serializer_class(criterion, many=False).data
        return JsonResponse({'criterion': criterion_data})
