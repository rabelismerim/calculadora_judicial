from base.coins.models import Coins
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from rates.models import Rate

from rates.schemas import RateSchema


class RateApi(AbstractViewApi):
    """HTTP methods for Rate"""
    http_method_names = ['post', 'get']
    serializer_class = RateSchema
    permission_classes = [permissions.IsAdminUser]
    model = Rate
    schema = AutoSchema(tags=["Rate"])

    query_params = [
        {
            "name": "valor",
            "field": "value__icontains",
            "in": "query",
            "required": False,
            "description": "Valor",
            "schema": {"type": "string"}
        }
    ]

    def post(self, request, *args, **kwargs):
        """Abstract method for default get model. Overide method in class for custom operation"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_rate = serializer.validated_data
        return JsonResponse({'rate': self.serializer_class(new_rate, many=False).data}, status=status.HTTP_201_CREATED)
