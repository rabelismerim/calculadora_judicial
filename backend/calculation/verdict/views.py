from calculation.verdict.models import TypeCalculation, Verdict
from calculation.verdict.schemas import VerdictSchema
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from core.abstract.views import CustomSchema as AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission


class VerdictApi(AbstractViewApi):
    """HTTP methods for verdict"""
    http_method_names = ['post', 'get']
    serializer_class = VerdictSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Verdict
    schema = AutoSchema(tags=["Calculation - Verdict"])

    query_params = [
        {
            "name": "sentença",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome da Sentença",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """
           Create verdict receiving a dict, return verdict detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_verdict = serializer.validated_data
        type_calculation = new_verdict.pop('type_calculation')
        new_verdict['type_calculation'] = TypeCalculation.objects.create(
            **type_calculation)
        verdict = self.model.objects.create(**new_verdict)
        return JsonResponse({'verdict': self.serializer_class(verdict, many=False).data}, status=status.HTTP_201_CREATED)
