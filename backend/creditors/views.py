from core.abstract.views import AbstractViewApi
from django.http import JsonResponse
from rest_framework import status
from rest_framework.schemas.openapi import AutoSchema
from rest_framework import permissions
from core.entity.models import Entity
from core.permission.views import CheckHasPermission
from creditors.schemas import CreditorSchema
from creditors.models import Creditor
from rates.models import Rate
from utils import get_user_model
User = get_user_model()


class AbstractCreditorApi(AbstractViewApi):
    """HTTP methods for creditor"""
    serializer_class = CreditorSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Creditor
    schema = AutoSchema(tags=["Creditor"])

    query_params = [
        {
            "name": "descrição",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": "Descrição do projeto",
            "schema": {"type": "string"}
        }
    ]

    def get_queryset(self):
        return {'recovering__project__engagement__users__user': self.request.user}

    def post(self, request, *args, **kwargs):
        """
           Create creditor receiving a dict, return creditor detail
        """
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)
        creditor = serializer.validated_data

        entity = creditor.pop('entity')
        rate = creditor.pop('rate')

        new_entity = Entity.objects.create(**entity)
        new_rate = Rate.objects.create(**rate)

        creditor['entity'] = new_entity
        creditor['rate'] = new_rate

        new_creditor = self.model.objects.create(**creditor)
        # return JsonResponse({'creditor': {}}, status=status.HTTP_201_CREATED)
        return JsonResponse({'creditor': self.serializer_class(new_creditor, many=False).data}, status=status.HTTP_201_CREATED)


class CreditorDetailApi(AbstractCreditorApi):
    """HTTP methods for creditor Detail"""
    http_method_names = ['get', 'post']


# class CreditorApi(creditor):
#     """HTTP methods for creditor"""
#     http_method_names = ['get', 'post']

#     def post(self, request, *args, **kwargs):
#         """
#            Create creditor receiving a dict, return creditor detail
#         """
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         creditor = serializer.validated_data

#         return JsonResponse({'creditor': self.serializer_class(creditor, many=False).data}, status=status.HTTP_201_CREATED)
