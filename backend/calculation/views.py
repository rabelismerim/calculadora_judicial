from calculation.models import Calculation
from calculation.schemas import CalculationSchema
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.permission.views import CheckHasPermission


class CalculationApi(AbstractViewApi):
    """HTTP methods for Calculation"""
    http_method_names = ['post', 'get']
    serializer_class = CalculationSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Calculation
    schema = AutoSchema(tags=["Calculation"])

    query_params = [
        {
            "name": "nome",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Nome do advogado",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """
           Create Calculation receiving a dict, return Calculation detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_calculation = serializer.validated_data
        calculation = self.model.objects.create(**new_calculation)
        return JsonResponse({'calculation': self.serializer_class(calculation, many=False).data}, status=status.HTTP_201_CREATED)
