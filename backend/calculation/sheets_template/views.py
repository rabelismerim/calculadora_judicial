from calculation.sheets_template.models import SheetsTemplate
from calculation.sheets_template.schemas import SheetsTemplateSchema
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _, doc


class SheetTemplateViewApi(AbstractViewApi):
    """HTTP methods for verdict"""
    http_method_names = ['get']
    serializer_class = SheetsTemplateSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = SheetsTemplate

    query_params = []
    docs = {
        'init': _("""Represents templates to publishing external sheets models to frontend.`, 
                """),
    }

    @doc(_("""This method handles GET requests for the view. It retrieves a list of objects sheets file using the given 
                calculation_id from the query parameters and serializes the result into JSON format before returning it
                 as an HTTP response. 

                    Returns:
                        JsonResponse: An HTTP response containing the serialized sheets file data retrieved.
                    """))
    def get(self, request, *args, **kwargs):
        calculation_id = kwargs.get('calculation_id')
        export_filter = kwargs.get('type_export')
        # statement = self.model.objects.filter(calculation_id=calculation_id)
        # statement_data = self.serializer_class(statement, many=True).data
        return JsonResponse({'excel': {''}})
