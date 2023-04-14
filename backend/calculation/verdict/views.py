from calculation.verdict.models import TypeCalculation, Verdict
from calculation.verdict.schemas import VerdictSchema
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _, doc


class VerdictDetailApi(AbstractViewApi):
    """HTTP methods for verdict"""
    http_method_names = ['get']
    serializer_class = VerdictSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Verdict

    query_params = []
    docs = {
        'init': _("""Represents additional sentences related to the process. They may include `material damages`, 
        `moral damages` among others.
                """),
    }

    @doc("""This method handles GET requests for the view. It retrieves a list of objects verdicts using the given 
                calculation_id from the query parameters and serializes the result into JSON format before returning it
                 as an HTTP response. 

                    Returns:
                        JsonResponse: An HTTP response containing the serialized verdicts data retrieved.
                    """)
    def get(self, request, *args, **kwargs):
        calculation_id = kwargs.get('calculation_id')
        statement = self.model.objects.filter(calculation_id=calculation_id)
        statement_data = self.serializer_class(statement, many=True).data
        return JsonResponse({'verdict': statement_data})


class VerdictApi(VerdictDetailApi):
    """HTTP methods for verdict"""
    http_method_names = ['post']

    @doc("""
           Create verdict receiving a dict, return verdict detail
        """)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_verdict = serializer.validated_data
        type_calculation = new_verdict.pop('type_calculation')
        new_verdict['type_calculation'] = TypeCalculation.objects.create(
            **type_calculation)
        verdict = self.model.objects.create(**new_verdict)
        return JsonResponse({'verdict': self.serializer_class(verdict, many=False).data},
                            status=status.HTTP_201_CREATED)
