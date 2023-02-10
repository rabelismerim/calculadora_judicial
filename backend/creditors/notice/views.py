from base.coins.models import Coins
from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from creditors.notice.models import Notice
from creditors.notice.schemas import NoticeSchema


class NoticeApi(AbstractViewApi):
    """HTTP methods for Notice"""
    http_method_names = ['post', 'get']
    serializer_class = NoticeSchema
    permission_classes = [permissions.IsAdminUser]
    model = Notice
    schema = AutoSchema(tags=["Creditors - Notice - Edital"])

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
        new_notice = serializer.validated_data
        coins = new_notice.get('coins')
        new_coins = Coins.objects.create(**coins)
        new_notice['coins'] = new_coins
        notice = self.model.objects.create(**new_notice)

        return JsonResponse({'notice': self.serializer_class(notice, many=False).data}, status=status.HTTP_201_CREATED)
