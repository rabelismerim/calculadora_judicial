from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from creditors.coins.models import Coins
from creditors.coins.schemas import CoinsSchema


class CoinsApi(AbstractViewApi):
    """HTTP methods for Coins"""
    http_method_names = ['post', 'get']
    serializer_class = CoinsSchema
    permission_classes = [permissions.IsAdminUser]
    model = Coins
    schema = AutoSchema(tags=["Creditors - Coins"])

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
           Create Coins receiving a dict, return Coins detail
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_coins = serializer.validated_data
        coins = self.model.objects.create(**new_coins)
        coins.save()
        return JsonResponse({'coins': self.serializer_class(coins, many=False).data}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """Get Coins details"""
        coinss = self.get_query()
        return JsonResponse({'coinss': coinss})
