from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from creditors.budgets.models import Budgets
from creditors.budgets.schemas import BudgetsSchema


class BudgetsApi(AbstractViewApi):
    """HTTP methods for Budgets"""
    http_method_names = ['post', 'get']
    serializer_class = BudgetsSchema
    permission_classes = [permissions.IsAdminUser]
    model = Budgets
    schema = AutoSchema(tags=["Creditors - Budgets"])

    query_params = [
        {
            "name": "description",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Descrição",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """
           Create Budgets receiving a dict, return Budgets detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_budgets = serializer.validated_data
        budgets = self.model.objects.create(**new_budgets)
        budgets.save()
        return JsonResponse({'budgets': self.serializer_class(budgets, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Budgets details"""
        budgetss = self.get_query()
        return JsonResponse({'budgetss': budgetss})
